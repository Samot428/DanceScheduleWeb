# DanceScheduleWeb

This app was built for dancers and dance trainers to help trainers manage their dance schedules, so they can focus on more important things.

---

## Login / Signup

As the user (dancer or dance trainer) signs in, he/she can choose whether they are a trainer or a dancer.  
Depending on this choice, the site redirects the user to two different pages.

---

## Trainer Page

The trainer can create clubs and then modify them.  
When the trainer opens his/her club, he/she can:

- Manage groups, where dance couples or dancers are placed
- Add trainers that he/she frequently uses in the club
- Manage days, where:
  - Start and end time of the day can be selected  
    (these times also affect the available time range of added trainers)
  - Trainers can be added (including group lessons aimed at specific groups)
  - Couples can be managed  
    (removed from the day or added — even couples not in the predefined groups, but the user must confirm this)
  - An **excel‑like editor** can be opened  
    - It is automatically filled with times and days  
    - Dancers can mark their daily availability  
    - These data are later used for schedule creation

---

## Schedule Creation

- An external file can be loaded, but it must be in a valid format (same as the excel‑like editor)
- Schedule settings can be managed:
  - Choose how couples should be ordered  
    (by group index, class level, or randomly)
  - Choose the day the schedule should be created for
  - Choose the file the data should be loaded from

### The Schedule Algorithm

- Couples are first scheduled so that couples from group **G1** do not have an individual lesson during a group lesson aimed at **G1**
- If such a schedule does not exist, some couples are joined together to free more space
- The same process is repeated without the group‑lesson restriction
- If all attempts fail, couples are sorted by difficulty (least available slots first)

If the schedule is successfully created, it can be downloaded as a **.csv** or **.txt** file so it can be sent to dancers via external apps.

