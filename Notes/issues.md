# Issues
### ARGM-ADV
There is a big problem with Adverbial modifier (ARGM-ADV), because sometimes it's how a second set of actors is
introduced (South Africa for the g-77/China Sentence 32). But sometimes this is not an actor and needs to
be added to the message, and sometimes neither. We can try added to the actor set if there's an actor in ARG-ADV

### Coref X said that they
41	kenya announced that it has withdrawn its offer to host the secretariat
kenya	withdrawn	its offer to host the secretariat


### Sentences with Nominal predicated which we removed from the test set
93	much of the discussion was on a proposal by the g-77/china to include research and development in the transport and energy sectors in the priority areas to be financed by the sccf
92	by the close of the day, though, the mood had turned sour for some following saudi arabia's insistence on amending the kyoto protocol at this cop/mop-- an issue many fear could prove among the most difficult to manage in the days ahead
91	on the cop decision, they agreed to a us proposal to note the need to streamline the review procedures in light of the additional review requirements for annex i parties that are also parties to the kyoto protocol
90	compliance: parties met for informal consultations on the adoption of the compliance mechanism and saudi arabia's proposal to amend the protocol
86	several annex i parties welcomed kazakhstan's proposal to be included in annex i. several non-annex i parties said further information was needed on kazakhstan's ability to fulfill annex i commitments
85	turkey's proposal to be removed from the annexes was supported by pakistan, the us, mexico and georgia
84	compliance (cop/mop): during the first meeting of the cop/mop contact group, co-chair danvivathana explained that the group's mandate covers two agenda items: the compliance committee's annual report; and croatia's appeal against a decision by the committee's enforcement branch
83	following a request for clarification from indonesia on the implications of germany's offer to confer legal capacity, the afb chair explained that germany had presented draft legislation, which involved passing the bill through parliament but that the process could take up to a year
81	some parties sought reassurance that this issue would not be conflated with, or prejudge the outcome of, discussions on the rules of procedure; and the proposal from papua new guinea and mexico to amend convention articles 7 and 18
80	given the g-77/china's opposition to an informal proposal to split negotiations into three issue clusters, participants wonder how president pronk will proceed
76	the dynamics within the basic group were still unclear to some, as was the broader response to the eu's proposal for how a package deal might emerge and its desire for a timetable towards a broader agreement
75	the final report will include the russian federation's objection to procedural steps embodied in the recommendation on the relationship between the montreal protocol and the fccc (fccc/sbsta/1998/crp.8)
48	these included a proposal from brazil for a new paragraph inviting parties to submit their views on the issue by 23 february 2007, although a separate proposal by brazil to establish an ad hoc special review team on the matter was not accepted


### Main type of errors
Preferred is not recognized by AllenNLP as a verb

ARGM ADV / sometimes we want to add it at the end, sometimes we don't want to ?
STUFF WITH SAID THAT sentence number 33
MAYBE DONT ADD IF ITS A SENTENCE w a verb // ADD IF NOT

WHY 
47	japan, with a number of other annex i parties, indicated that he did not consider reporting under article 3.14 to be mandatory, and could not accept a link to mechanisms eligibility.
he	not accept	a link to mechanisms eligibility
japan	indicated	that he did not consider reporting under article 3.14 to be mandatory, and could not accept a link to mechanisms eligibility

48	latvia: indulis emsis, state minister for the environment, called for increased commitments for developed countries, adding that latvia cannot accept new commitments.
latvia	not accept	new commitments
latvia	called	for increased commitments for developed countries

55	the us supported one decision for both and, with japan, opposed compensation for adverse effects.
japan	opposed	compensation for adverse effects
united states	opposed	compensation for adverse effects
united states	supported	one decision for both

GOLDSET WAS 
united states	supported	one decision for both and, with japan, opposed compensation for adverse effects


83	yugoslavia, opposed by the eu, said it could not support croatia's 1990 baseline proposal
european union	support	croatia's 1990 baseline proposal
yugoslavia	not support	croatia's 1990 baseline proposal

45	on the current negotiations at cop-7, switzerland said it could not accept changes that weaken the bonn agreements, and stated that no country can shirk its responsibilities.
switzerland	stated	that no country can shirk its responsibilities on the current negotiations at cop-7
And in the goldset 
switzerland	stated	on the current negotiations at cop-7 that no country can shirk its responsibilities