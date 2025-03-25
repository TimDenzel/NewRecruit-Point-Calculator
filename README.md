<h1>How to use the NewRecruit-Point-Calculator.exe for Warhammer Armies Project</h1>

This Tool was developed, so Users of the NewRecruit Page can calculate the Battle-Result and -Losses easier.
You can add your Army manually by opening the Application and, using the 'Add Row'-Button, add each of your Units to the
Calculator.
If you are using the NewRecruit Webpage, you can use the following Paragraph to import your armies.

<h2>How to import your Army from NewRecruit</h2>

1. Download your army as a .json File from NewRecruit via the Export-Button
2. Open up the **NewRecruit-Point-Calculator.exe**
3. Go to 'File' and press 'Import File', A dialog-window will open, where you can choose your .json file you exported
   from NewRecruit.
4. Wait for a short while as it takes a few seconds before your army is loaded into the calculator.
5. Your army should now be loaded and you can start calculating! For how to work with the calculator, refer to the next
   paragraph.

<h2>How to work with the NewRecruit-Point-Calculator</h2>

The Calculator is split in the following columns:

| **Column**                           | **Description**                                                                                                                                                                                                                                   |
|--------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Name**                             | Displays the name of your units                                                                                                                                                                                                                   |
| **General?**                         | Displays if the Unit is the General of the army                                                                                                                                                                                                   |
| **Points**                           | Displays the total cost of the Unit                                                                                                                                                                                                               |
| **Start-Wounds or -Models**          | Displays with how many wounds a Character and how many Models a Unit starts                                                                                                                                                                       |
| **Lost Wounds or Models**            | Displays how many Wounds or Models a Character or Unit has lost during the engagement                                                                                                                                                             |
| **Fleeing**                          | Calculates how many Points are gained for the Unit/Character if it's fleeing. The formula refers to the Warhammer Armies Core Rulebook, where if a unit is fleeing and at or under 50% unit strength, the unit provides 75% of their total points |
| **Standard lost**                    | Can be checked if the Unit/Character has lost its Standard in Close Combat, adding 25 extra Points                                                                                                                                                |
| **Battle Standard lost**             | Can be checked if the Battle Standard Bearer has lost the Battle Standard in Close Combat, adding 100 extra Points, this doesn't stack with the standard, so checking Battle-Standard for a character will be enough                              |
| **Total Points from Unit/Character** | Calculates the total Value the enemy gained from this Unit/Character                                                                                                                                                                              |

By changing the checkboxes and updating the **Lost Wounds or Models**-Entries the calculator will update the **Points
Lost**-Entry on the bottom right.

Beneath the calculator is the control-panel which provides the following utilities:

| **Widgets**      | **Description**                                                                                             |
|------------------|-------------------------------------------------------------------------------------------------------------|
| **Add Row**      | A Button to add new rows to your army-list or a custom army-list                                            |
| **Load Army**    | A Button to either reload your edited army-list or to load your manually added army-list for the calculator |
| **Reset**        | A Button to reset the whole calculator. It won't ask you to confirm, so be careful                          |
| **Army:**        | The Name of your army-list.                                                                                 |
| **Army Points:** | The Total Points spent on your army and the registered Point-maximum of your army                           |
| **Lost:**        | The calculated losses of your army                                                                          |

Above the calculator is the Menu-Bar. It currently only provides a File-Menu with the following options
| **Widgets**                      | **Description**                                                                 |
|----------------------------------|---------------------------------------------------------------------------------|
| **Load File**   | Loads previously saved .csv-file. |
| **Save File**   | Saves the currently displayed army in a .csv-file |
| **Import File** | Loads a .json which has been exported from NewRecruit Warhammer Armies Project |
| **Export File** | Exports the currently displayed army to a custom .json for further processing if needed. This is
final, as you currently cant load the .json back into the NewRecruit-Point-Calculator.exe |
| **Exit**        | Exits the Application |

<h2>Contact</h2>

Discord Contact for Bugs: denzel1410
This is a fan-made application. All images and logos are owned by their respective companies and only used in a
non-commercial way.
