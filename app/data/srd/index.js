const abilityScores       = require('./abilityScores.json');
const classes             = require('./classes.json');
const conditions          = require('./conditions.json');
const damageTypes         = require('./damageTypes.json');
const equipment           = require('./equipment.json');
const equipmentCategories = require('./equipmentCategories.json');
const features            = require('./features.json');
const languages           = require('./languages.json');
const levels              = require('./levels.json');
const magicSchools        = require('./magicSchools.json');
const monsters            = require('./monsters.json');
const proficiencies       = require('./proficiencies.json');
const races               = require('./races.json');
const skills              = require('./skills.json');
const spellcasting        = require('./spellcasting.json');
const spells              = require('./spells.json');
const startingEquipment   = require('./startingEquipment.json');
const subclasses          = require('./subclasses.json');
const subraces            = require('./subraces.json');
const traits              = require('./traits.json');
const weaponProperties    = require('./weaponProperties.json');

const data = {
    abilityScores,
    classes,
    conditions,
    damageTypes,
    equipment,
    equipmentCategories,
    features,
    languages,
    levels,
    magicSchools,
    monsters,
    proficiencies,
    races,
    skills,
    spellcasting,
    spells,
    startingEquipment,
    subclasses,
    subraces,
    traits,
    weaponProperties,
};

module.exports = {
    data,
};
