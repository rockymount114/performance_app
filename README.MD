# How to use

### City Performance Management System
This application is designed to help city departments track and manage their performance metrics and initiatives.

## User Registration
All users must be registered with a valid city email address.
After registration, an administrator will assign each user to the appropriate department.
Department Data Entry
Once assigned to a department, users can add records for the following data elements:

Mission
Overview
Objectives
Focus Areas
Initiatives
Quarterly Data
For each Objective and Initiative, users can enter quarterly data updates. When a user clicks on an Objective or Initiative, they will be able to view and edit the associated quarterly data details.

## Adding New Data Elements
If a department needs to add more data elements, such as new Objectives or Focus Areas, users can click the "+" sign to create a new entry. However, these new entries will be flagged and require approval from the Performance Chief before becoming visible to other users.

Note: Adding new Strategic Initiatives does not require approval.

## Data Approval Process
When a user adds a new Objective or Focus Area, it will be flagged for review. Once the Performance Chief approves the new entry, the flag will automatically disappear, and the data will be visible to all users in that department.

05/02/24:
    1. Added password reset function
    2. Fixed profile photo upload
    3. Added yearly rate for PDF
    4. Yearly rate on Quartlery data page, changed /4 to depends on how many quarter data has been input, such as /2 if only has q1 & q2 data



TODDS:

1. dashboard 
    a. lock quarterly input based on date.

2. Quarterly Data
    a. when missing input data, then email Mamadou, then Mamadou can unlock it for a period of time to allow user to input
    b. need color coding for percentages??? such as 0-25% red, 25-50% orange, 50-75% blue, 75-100% green

3. One department if has more than 3 people register, add a flag to point who is the data input person???

4. Approval page, 
    a. column needs to adjust, such as title col to more wide?
    b. currently the filter is 2023 as default, needs to change

5. Measure -- added a flag (is_number), do we need a flag to show it on dashboard?

6. PDF
    a. for dept, report title needs to add Fiscal Year