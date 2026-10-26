# Method Properties Manager

By Elliott Jensen, Technical Services Engineer, 4D Inc.

Technical Note 24-12

## Abstract

The Method Properties Manager is a powerful tool designed to simplify the process of viewing and editing method properties. While working with large numbers of methods in 4D can sometimes feel overwhelming, this component offers a solution by allowing developers to easily view all methods with a specific property and make targeted adjustments. It streamlines workflows, making it easier to manage and modify method properties efficiently.

## Introduction

Managing method properties is an essential part of the 4D development process. These properties control important access and security conditions of an application, like which methods are preemptive capable or which methods are published and made accessible through the web. Having an effective tool for developers to manage these properties can streamline the design process and improve the experience of the developer. Currently, managing method properties can be difficult, especially when working with applications that have many methods. The purpose of the Properties Manager Component is to make viewing and editing properties easier. With this tool the developer will be able to view all methods that have a certain property and edit properties of multiple selected methods at once.

## Overview of Existing Feature in 4D

Each method in 4D has ten different method properties that 4D developers can use in their application. They can be accessed and modified via the Explorer or the Code Editor:

![](fig-01)

Currently 4D has two techniques for accessing the above window. Developers can right click on a property within the file explorer and select “Edit Properties” to pull up the window.

![](fig-02)

Within the code editor, developers can also open the Method Properties window by clicking a button in the code editor.

![](fig-03)

Neither of these techniques are effective when there are many methods that have properties that need to be viewed or modified. Both options require the developer to select each method individually to view its properties and there is no way to view all methods with a certain property or to apply modifications to multiple method properties at once.

## Batch Setting of Attributes

4D’s current feature for modifying multiple method properties at once, the batch setting of attributes tool, has limitations that the Method Properties Manager seeks to address. The batch setting of attributes tool is effective if the developer has a naming convention for their methods that corresponds to the properties of those methods. For example, if every method that will be published on the web begins with “Web”. In this case the developer can enter “Web@” as the matching string and the batch setting of attributes tool will update all methods with a method name that begins with “Web” with the property specified in the dropdown menu. However, if a developer did not use a naming convention like this, or their methods have multiple properties that do not cleanly map to their names, then the developer will run into difficulties when using this tool.

![](fig-04)

The Method Properties Manager seeks to address these limitations by allowing the developer to have a list of methods that they can filter. Instead of applying or removing a property based on matching characters in the method name, developers can select multiple methods from the list that they want to edit.

## Configuration & Setup

To run the Method Properties Manager component you must be running locally and in interpreted mode. If one does not exist already, create a folder named "Components" in the project folder where the Properties Manager Component will be installed. Then drag the ".4dbase" file into the folder. After this, run the project in 4D standalone, select execute and run "open_property_manager".

![](fig-05)

## Using the Component

On the left method names are displayed along with the number of methods that match the current filter. Double clicking on a method will open the code editor for that method. Holding down shift will allow you to select multiple methods.

![](fig-06)

On the right, a property can be selected and the component will display all methods that have this property.

![](fig-07)

Below this, a property can be selected to edit. Most of the properties are stored as a Boolean and can be switched between "True" and "False" using the "Apply" and "Remove" button respectively.

![](fig-08)

The preemptive property is not stored as a Boolean and instead can be switched between the three values "capable", "incapable" and "indifferent".

![](fig-09)

## Implementation

Each method file stored in the project folder begins with a “//%attributes = {}” that stores the different properties of a method. This line is hidden in the 4D method editor but can be viewed in the contents of a .4dm file with a different text editor like Visual Studio Code.

![](fig-10)

The properties denoted by this line can be read and written to programmatically using the METHOD GET ATTRIBUTE and METHOD SET ATTRIBUTE commands. The component uses these commands to display and edit method properties.

## Conclusion

This technical note described the Method Property Manager Component. It discussed how the components is intended to address the difficulties caused by editing properties in the file explorer. It explained how the components features allow the user to easily view methods that have a specific property and edit multiple methods at the same time.

## References

**Command** METHOD GET ATTRIBUTE - https://doc.4d.com/4Dv20/4D/20.4/METHOD-Get-attribute.301-7026380.en.html

**Command** METHOD SET ATTRIBUTE - https://doc.4d.com/4Dv20/4D/20.4/METHOD-SET-ATTRIBUTE.301-7026395.en.html
