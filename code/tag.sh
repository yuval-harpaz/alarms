#!/usr/bin/bash
# Tag a map release in both repos, and publish what the tag points at.
#
#     code/tag.sh                    # patch bump, build, push both, tag both
#     code/tag.sh -n                 # print every step, run none of them
#     code/tag.sh -v minor
#     code/tag.sh -v 2.0.0 -m "four levels, two colourings"
#     code/tag.sh -P                 # build and tag, push nothing: a rehearsal
#     code/tag.sh -V                 # tag only: no build, no push
#
# The tag is the same name in both repos, because the map is the two of them
# together: the code that built it and the html it wrote. Tagging one without
# the other leaves a version nobody can rebuild.
#
# The second repo is wherever $WEBSITE points -- the same variable the build
# writes into -- so this script never has to name it.
#
# Order is forced by the build, twice over. iron_swords_map.py reads
# oct7database.csv from github, not from the working copy, so alarms has to be
# pushed before the build runs, or the build is around the old csv. And it
# stamps the page with `git describe`, so the alarms tag has to exist before
# the build, or the html carries the previous version while the release is
# called this one. Hence: push, tag alarms, build, commit the site.
#
# The tags are made locally and pushed at the very end, so a build that fails
# leaves nothing anyone has seen. The trap deletes them on the way out. That
# is also what -P leans on: a rehearsal leaves tags only you can see, and
# `git tag -d` undoes them.
set -euo pipefail

ALARMS=~/alarms
PREFIX=map-v
PY="$ALARMS/.venv/bin/python"

bump=patch      # or major, minor, or an explicit X.Y.Z
message=        # default is built from the version once it is known
dry=0
build=1
push=1

die() { echo "tag.sh: $*" >&2; exit 1; }

# What a repo is called in the output. The site is named by its role rather
# than by the directory it happens to live in.
label() { [ "$1" = "$ALARMS" ] && echo alarms || echo "the site"; }
run() {
    if [ "$dry" -eq 1 ]; then
        printf '  %q' "$@"; printf '\n'
    else
        "$@"
    fi
}

usage() {
    sed -n '2,16p' "$0" | sed 's/^# \?//'
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
        -P|--no-push) push=0 ;;
        -h|--help) usage 0 ;;
        *) die "unknown option '$1' (-h for usage)" ;;
    esac
    shift
done

# ------------------------------------------------------------------- repos

# The site is a checkout and $WEBSITE is a directory inside it, so the repo
# root comes from git rather than from a path spelled out here.
[ -n "${WEBSITE:-}" ] || die "WEBSITE is not set -- it is where iron_swords_map.py writes"
[ -d "$WEBSITE" ] || die "WEBSITE points at '$WEBSITE', which is not a directory"
SITE=$(git -C "$WEBSITE" rev-parse --show-toplevel 2>/dev/null) ||
    die "WEBSITE ('$WEBSITE') is not inside a git checkout"
SITE_BRANCH=$(git -C "$SITE" rev-parse --abbrev-ref HEAD)

# ---------------------------------------------------------------- version

# What the remote of a repo already carries. Published is the only thing that
# counts: a number is spent when someone else can see it, not when it exists
# in this checkout.
remote_tags() {
    git -C "$1" ls-remote --tags origin "$PREFIX*" 2>/dev/null |
        sed 's|.*refs/tags/||; s|\^{}$||' | sort -u
}

published=$( { remote_tags "$ALARMS"; remote_tags "$SITE"; } | sort -u )

# The highest tag either remote carries, so a tag that reached only one of
# them still counts and the next number cannot collide with it.
latest=$( echo "$published" |
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

grep -qx "$tag" <<< "$published" &&
    die "$tag is already published -- pick another with -v"

branch=$(git -C "$ALARMS" rev-parse --abbrev-ref HEAD)
[ "$branch" = master ] || die "alarms is on '$branch', not master"

echo "$tag  ($message)"
[ "$dry" -eq 1 ] && echo "dry run, nothing below is executed:"

# ------------------------------------------------------------------ publish

# Which repos hold a local tag this run made, so the trap knows what to undo.
# A tag that was already pushed is not in here: past that point there is
# nothing to take back quietly.
tagged=()

cleanup() {
    status=$?
    [ "$status" -eq 0 ] && return
    for repo in "${tagged[@]:-}"; do
        [ -n "$repo" ] || continue
        echo "undoing the local $tag in $(label "$repo")" >&2
        git -C "$repo" tag -d "$tag" >/dev/null 2>&1 || true
    done
    echo "tag.sh: stopped, nothing was published" >&2
}
trap cleanup EXIT

# A local map-v* tag no remote has is a leftover: a -P rehearsal, or a run
# that stopped before its push. It holds a number nobody ever saw, so it is
# taken back rather than worked around.
for repo in "$ALARMS" "$SITE"; do
    while read -r stale; do
        [ -n "$stale" ] || continue
        grep -qx "$stale" <<< "$published" && continue
        echo "reclaiming $stale in $(label "$repo"): no remote has it"
        run git -C "$repo" tag -d "$stale"
    done < <(git -C "$repo" tag --list "$PREFIX*")
done

# Whatever is in the tree is what the tag will point at, so it is committed
# here rather than sent back to you. The site is left alone: the build is
# about to rewrite it.
if [ -n "$(git -C "$ALARMS" status --porcelain)" ]; then
    echo "committing alarms:"
    git -C "$ALARMS" status --short | sed 's/^/    /'
    run git -C "$ALARMS" add -A
    run git -C "$ALARMS" commit -q -m "$message"
fi

if [ "$push" -eq 1 ]; then
    echo "pushing alarms, so the build reads this csv and not the last one"
    run git -C "$ALARMS" push origin master
fi

# Before the build, so `git describe` inside iron_swords_map.py stamps the
# page with this version rather than the last one.
echo "tagging alarms"
run git -C "$ALARMS" tag -a "$tag" -m "$message"
[ "$dry" -eq 1 ] || tagged+=("$ALARMS")

if [ "$build" -eq 1 ]; then
    echo "building the map into $WEBSITE"
    [ -x "$PY" ] || die "no venv python at $PY"
    run "$PY" "$ALARMS/code/iron_swords_map.py"
fi

if [ "$push" -eq 1 ]; then
    if [ "$dry" -eq 1 ] || [ -n "$(git -C "$SITE" status --porcelain)" ]; then
        echo "committing and pushing the site"
        run git -C "$SITE" add -A
        run git -C "$SITE" commit -m "map v$version"
        run git -C "$SITE" push origin "$SITE_BRANCH"
    else
        echo "the site is unchanged by the build, nothing to commit"
    fi
fi

# The site is tagged after its commit, so the tag names the html the build wrote.
echo "tagging the site"
run git -C "$SITE" tag -a "$tag" -m "$message"
[ "$dry" -eq 1 ] || tagged+=("$SITE")

# --------------------------------------------------------------------- push

# Last, and only once both repos are in the state the tag describes.
if [ "$push" -eq 1 ]; then
    for repo in "$ALARMS" "$SITE"; do
        echo "pushing $tag to $(label "$repo")"
        run git -C "$repo" push origin "$tag"
    done
    tagged=()
fi

echo "done: $tag on alarms and the site"
