#!/usr/bin/bash
# Tag a map release in both repos, and publish what the tag points at.
#
#     code/tag.sh                    # patch bump, build, push both, tag both
#     code/tag.sh -n                 # print every step, run none of them
#     code/tag.sh -v minor
#     code/tag.sh -v 2.0.0 -m "four levels, two colourings"
#     code/tag.sh -V                 # tag only: no build, no push
#
# The tag is the same name in alarms and misc, because the map is the two of
# them together: the code that built it and the html it wrote. Tagging one
# without the other leaves a version nobody can rebuild.
#
# Order is forced by the build. iron_swords_map.py reads oct7database.csv from
# github, not from the working copy, so alarms has to be pushed before the
# build runs or the build is around the old csv. The build then writes into
# misc, which is why misc is committed after it and not before.
set -euo pipefail

ALARMS=~/alarms
MISC=~/misc
PREFIX=map-v
PY="$ALARMS/.venv/bin/python"

bump=patch      # or major, minor, or an explicit X.Y.Z
message=        # default is built from the version once it is known
dry=0
build=1
push=1

die() { echo "tag.sh: $*" >&2; exit 1; }
run() {
    if [ "$dry" -eq 1 ]; then
        printf '  %q' "$@"; printf '\n'
    else
        "$@"
    fi
}

usage() {
    sed -n '2,15p' "$0" | sed 's/^# \?//'
    exit "${1:-0}"
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        -v|--version)
            [ "$#" -ge 2 ] || die "-v wants a version or major|minor|patch"
            bump="$2"; shift
            ;;
        -m|--message)
            [ "$#" -ge 2 ] || die "-m wants a message"
            message="$2"; shift
            ;;
        -n|--dry-run) dry=1 ;;
        -V|--tag-only) build=0; push=0 ;;
        -B|--no-build) build=0 ;;
        -h|--help) usage 0 ;;
        *) die "unknown option '$1' (-h for usage)" ;;
    esac
    shift
done

# ---------------------------------------------------------------- version

# The highest tag either repo carries, so a tag that reached only one of them
# still counts and the next number cannot collide with it.
latest=$( { git -C "$ALARMS" tag --list "$PREFIX*"
            git -C "$MISC" tag --list "$PREFIX*"; } |
          sed "s/^$PREFIX//" |
          grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' |
          sort -t. -k1,1n -k2,2n -k3,3n | tail -1 )
latest=${latest:-0.0.0}

case "$bump" in
    major|minor|patch)
        IFS=. read -r major minor patch <<< "$latest"
        case "$bump" in
            major) major=$((major + 1)); minor=0; patch=0 ;;
            minor) minor=$((minor + 1)); patch=0 ;;
            patch) patch=$((patch + 1)) ;;
        esac
        version="$major.$minor.$patch"
        ;;
    *)
        version=${bump#"$PREFIX"}          # -v map-v2.0.0 is not an error
        version=${version#v}
        [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] ||
            die "bad version '$bump': want X.Y.Z, or major|minor|patch"
        ;;
esac

tag="$PREFIX$version"
message=${message:-"map v$version published"}

for repo in "$ALARMS" "$MISC"; do
    git -C "$repo" rev-parse -q --verify "refs/tags/$tag" >/dev/null &&
        die "$tag already exists in $repo"
done

# ------------------------------------------------------------------ checks

# A tag on a dirty tree points at something that was never tested. misc is
# allowed to be dirty here: the build is about to rewrite it anyway.
if [ -n "$(git -C "$ALARMS" status --porcelain)" ]; then
    [ "$dry" -eq 1 ] ||
        die "alarms has uncommitted changes -- commit them first, they are what the tag points at"
    echo "warning: alarms has uncommitted changes, a real run would stop here"
fi

branch=$(git -C "$ALARMS" rev-parse --abbrev-ref HEAD)
[ "$branch" = master ] || die "alarms is on '$branch', not master"

echo "$tag  ($message)"
[ "$dry" -eq 1 ] && echo "dry run, nothing below is executed:"

# ------------------------------------------------------------------ publish

if [ "$push" -eq 1 ]; then
    echo "pushing alarms, so the build reads this csv and not the last one"
    run git -C "$ALARMS" push origin master
fi

if [ "$build" -eq 1 ]; then
    echo "building the map into misc"
    [ -x "$PY" ] || die "no venv python at $PY"
    run "$PY" "$ALARMS/code/iron_swords_map.py"
fi

if [ "$push" -eq 1 ]; then
    if [ "$dry" -eq 1 ] || [ -n "$(git -C "$MISC" status --porcelain)" ]; then
        echo "committing and pushing misc"
        run git -C "$MISC" add -A
        run git -C "$MISC" commit -m "map v$version"
        run git -C "$MISC" push origin main
    else
        echo "misc is unchanged by the build, nothing to commit"
    fi
fi

# --------------------------------------------------------------------- tag

for repo in "$ALARMS" "$MISC"; do
    echo "tagging $(basename "$repo")"
    run git -C "$repo" tag -a "$tag" -m "$message"
    run git -C "$repo" push origin "$tag"
done

echo "done: $tag on alarms and misc"
