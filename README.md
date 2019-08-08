*Reference List Generation*

usage

>$ ./prepare_cube_uploads

or

>$ ./prepare_cube_uploads [CUBE_ENV]

where CUBE_ENV is configured in cube_config.json

Use this library to specify reference cubetutor lists for a given environment,
then fetch those lists and create pipe-delimited exports

ref_lists.csv and card_reference.csv

to be pasted into the cube management sheets tool. Additional cards can be
maintained in the card_reference sheet by means of cubes_raw.txt and always_include.txt.

cube_raw.txt can be pasted from the Decks and/or Lists sheet.
always_include.txt is to be maintained manually. Cards may be removed after they appear on a list.

**Default Behavior**

