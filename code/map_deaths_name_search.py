import numpy as np

def group_locs(df):
    replace = [['בכניסה לעלומים'], ['ביה"ח שיפא'], ['מערבית לצומת גמה', 'צומת גמה'], ['סמוך לצומת גמה', 'צומת גמה'], ['מיגונית בצומת גמה', 'צומת גמה'],
               ['צומת בארי'], ['מיגונית בצומת רעים', 'צומת רעים'], ['סמוך לצומת רעים', 'צומת רעים'], ['חאן יונס'],['מיגונית חניון רעים', 'פסטיבל נובה'],
               ['רצועת עזה', 'רצועת עזה, לא פורסם מיקום מדוייק'], ['דיר אל בלח'], ['מיגונית מפלסים','סמוך למפלסים']]  #
    for uu in replace:
        df.loc[df['location'].str.contains(uu[0]), 'location'] = uu[-1]  # -1 allows for pairs, search term + what to change into
    return df

name_search_html = """<div class="autocomplete-drop-down">
                <div class="Names-input-container">
                  <input class="Names-input" placeholder="שם משפחה ו\או פרטי" type="text">
                  <div class="input-underline"></div>
                  <span class="input-arrow">&#9662;</div>
                </div>
              
                <div class="Names-list-container">
                  <ul class="Names-list">
                    <li>&nbsp;</li>
                  </ul>
                </div>
              </div>"""
name_search_style = """<style>
                html {
  padding: 20px;
  font-family: roboto, helvetica, arial, sans-serif;
  font-size: 16px;
}

input {
  font-size: 16px;
}

.autocomplete-drop-down {
  position: relative;
  width: 30vw;
  direction:rtl;
}

.Names-input,
.Names-list {
  border: none;
  box-sizing: border-box;
  width: 30vw;
  direction:rtl;
  list-style-type: none;
}
.cd__main{
display: block !important;
}
.Names-input-container {
  height: 2.5rem;
  position: relative;
}

.Names-input {
  height: 2.5rem;
  padding: 1em 0.5em;
  position: relative;
  transition: outline 0.2s ease;
  transition-delay: 0.2s;
}
.Names-input:focus + .input-underline {
  transform: scaleY(0);
}
.Names-input:focus ~ .input-arrow {
  transform: rotate(180deg);
}

.input-underline {
  background: #000;
  bottom: 0;
  content: "";
  height: 2px;
  left: 0;
  position: absolute;
  transform-origin: center bottom;
  transition: transform 0.3s ease;
  width: 30vw;
}

.input-arrow {
  position: absolute;
  left: 0.5em;
  top: calc(50% - 0.5rem);
  transition: transform 0.3s ease;
}

.Names-list-container {
  box-shadow: 0 8px 15px 0 rgba(33, 33, 33, 0.2);
  opacity: 0;
  position: relative;
  transform: scaleY(0);
  visibility: hidden;
  transform-origin: center top;
  transition: all 0.3s ease;
  width: 30vw;
}
.Names-list-container.visible {
  opacity: 1;
  transform: scaleY(1);
  visibility: visible;
}

.Names-list {
  align-content: middle;
  display: flex;
  flex-wrap: wrap;
  max-height: 11.5em;
  overflow-x: hidden;
  overflow-y: scroll;
  width: 30vw;
}

.name {
  cursor: pointer;
  padding: 0.5em 0;
  transition: background 0.5s ease;
  width: 30vw;
}
.name:hover {
  background: #CCC;
}
.name span {
  box-sizing: border-box;
  display: inline-block;
}

.name--location {
  padding: 0 1em;
  width: 18%;
}

.name--name {
  width: 78%;
}
            </style>"""
name_search_script = """
const filterNamesOnChange = event => {
  const value = event.target.value.toLowerCase();
    if (value.length < 3) {
        return;
    }
    const result = NamesByLocation.filter(nameObject => {
    const location = nameObject.location || '';
    const name = nameObject.name || '';
    const nameString = `${location} ${name}`;

    return nameString.toLowerCase().includes(value);
  });

  generateNamesList(result);
};

const addEventListenerToNames = () => {
  const NamesInput = document.querySelector('.Names-input');
  const nameListItems = document.querySelectorAll('.name');
  let nameListItemIndex = 0;
  const nameListItemILength = nameListItems.length;

  for (nameListItemIndex; nameListItemIndex < nameListItemILength; nameListItemIndex++) {
    const nameListItem = nameListItems[nameListItemIndex];

    nameListItem.addEventListener('mousedown', event => {
      event.preventDefault();
      event.stopPropagation();

      const value = event.currentTarget.getAttribute('data-name');
      NamesInput.value = value;

      const coords = LocationByName[event.currentTarget.getAttribute('data-location')];
      const zoom = 13;

      MAP_NAME.setView([coords['lat'], coords['long']], zoom);

      filterNamesOnChange({ target: { value } });

      NamesInput.focus();
    });
  }
};

const createnameListItem = ({ name = '', location = '' }) =>
`<li class="name" data-location="${location}" data-name="${name}"><span class="name--name">${name}</span> <span class="name--location">${location}</span></li>`;


const generateNamesList = NamesArray => {
  const NamesList = document.querySelector('.Names-list');
  NamesList.innerHTML = '';

  const NamesLength = NamesArray.length;

  for (let nameIndex = 0; nameIndex < NamesLength; nameIndex++) {
    NamesList.innerHTML += createnameListItem(NamesArray[nameIndex]);
  }

  addEventListenerToNames();
};

document.addEventListener("DOMContentLoaded", () => {
  const NamesInput = document.querySelector('.Names-input');

  NamesInput.addEventListener('keyup', filterNamesOnChange);

  NamesInput.addEventListener('focus', () => {
    const NamesList = document.querySelector('.Names-list-container');
    NamesList.classList.add('visible');
  });

  NamesInput.addEventListener('blur', event => {
    const NamesList = document.querySelector('.Names-list-container');
    NamesList.classList.remove('visible');
  });
});
"""

def clean(text):
    text = text.replace('"', '&quot;')
    return text

def name_data_js(names, coo, name_col='fullName'):
    if name_col =='fullName':
        personal_loc = names['location']
    else:
        personal_loc = []
        for plh in names['location']:
            loc_row = np.where(coo['name'] == plh)[0][0]
            personal_loc.append(coo['eng'][loc_row])
    data = "\n".join([f'{{name: "{clean(name)}", location: "{clean(location)}"}},' for name, location in zip(names[name_col], personal_loc)])
    return f"const NamesByLocation = [{data}];\n"

def location_data_js(coo, name_col='fullName'):
    if name_col == 'fullName':
        loc_col = 'name'
    else:
        loc_col = 'eng'
    data = "\n".join([f'"{clean(name)}": {{"lat": {lat}, "long": {long}}},' for name, lat, long in zip(coo[loc_col], coo['lat'], coo['long'])])
    return f"const LocationByName = {{{data}}};\n"

def name_search_addon(names, coo, map_name, name_col='fullName'):
    return name_search_html + name_search_style + "<script>" + name_data_js(names, coo, name_col=name_col) + location_data_js(coo, name_col=name_col) + name_search_script.replace("MAP_NAME", map_name) + "</script>"