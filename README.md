# DanceScheduleWeb
This App was built for dancers and dance trainers with of helping the trainers with their dance schedules, so they can focus on more important things.

Login / Signup:
As the user (dancer/dance trainer) signs in, he/she can choose, wheter is he/she a trainer or dancer. Depending on this choice, the site redirects the user to two different pages.

Trainer Page:
The Trainer can create clubs and then modified them. When the Trainer opens his/her club, he/she can:
    - manage his/her groups, where dance couples or dancers are placed
    - add trainers, that he/she frequently uses in the club
    - manage his/her days, where:
        - start and end time of the day can be selected (depending on these times, the start/end time of the added trainers will also change)
        - trainers can be added (also with group lessons, which can be aimed for some specific groups defined before)
        - couples can be managed (removed from the day or added - also couples that aren't in the groups mentioned above, but the user has to confirm this addition)
        - excel-like editor can beopened. This editor is automatically set with times and days so the trainer doesn't have to do it manually. Here the dancers can mark their daily                   availability, so these data can be later used for the schedule creation
    - schedule creation:
      - an external file can be loaded, but it has to be in valid format (like the excel-like editor)
      - schedule settings can be managed:
        - Whether a user wants to order the couples by group index (the lowest group index as first), by class level or randomly
        - Choose a day that the schedule should be made for
        - Choose the fail that the data should be loaded from
      THE SCHEDULE ALGORITHM:
        - couples are first tryed to be scheduled such as, that the couples lets say from group G1 don't have an individual lesson durin a group lesson that is aimed for this group G1
        - if such a schedule doesn't exists, the some couples are tryed to be joined together, so more space is left for other unscheduled couples
        - the same process is repeated, but without the restriction for the not individual lesson during group lesson
        - if all these schedules fails, the couples are sorted in a way of the hardest couples to schedule as first (with least available slots)
      If the schedule is created it can be downloaded as a .csv or .txt file, so it can be sent to the dancers VIA some external app
      -
