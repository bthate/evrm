# This file is placed in the Public Domain.
#
# OTP-CR-117/19/001 otp.informationdesk@icc-cpi.int https://genocide.rtfd.io

"""| Information and Evidence Unit
| Office of the Prosecutor
| Post Office Box 19519
| 2500 CM The Hague
| The Netherlands
| or sent by email to otp.informationdesk@icc-cpi.int

Hello Office of the Prosecutor,

i write you in the context of communications and claims under art.15 of the Rome Statute. I want to inform the prosecutor that the king of the netherlands and his government are commiting 3 of the 5 crimes defined in the Rome Statute. I know the statute only provides juridistion over genocide claims concerning nationalities or crimes based on etnicity. The crimes i talk about are on generic parts of the population like all elderly of all psychiatric patients. The kingdom of the netherlands uses law to provide “care” with entails adminstering poison instead of non harmfull substances (what medicine should be).

There is proof the medication used in forced treatements in the netherlands are poison.

| *   haloperiodol (haldol) - https://echa.europa.eu/substance-information/-/substanceinfo/100.000.142
| *   clozapine (leponex) - https://echa.europa.eu/substance-information/-/substanceinfo/100.024.831
| *   olanzapine (zyprexa) - https://echa.europa.eu/substance-information/-/substanceinfo/100.125.320
| *   aripriprazole (abilify) https://echa.europa.eu/substance-information/-/substanceinfo/100.112.532

The dutch government has introduced three new forced care laws, the Wfz (wet forensische zorg) for criminals, the WvGGZ (Wet verplichte GGZ) for the disturbed and addicted and the Wzd (Wet zorg en dwang) for the handicapped.

Instead of groups with an nationaliteit or etnicity the laws targets the following victim groups in the netherlands:

| *   verslaafden (addicts)
| *   bejaarden (elderly)
| *   ggz patienten (psychiatric patients)
| *   criminelen (criminials)
| *   gehandicapten (handicapped)

I informed the eerste kamer (who votes for the laws to be signed by the king) about the fact that these medicine as poison before the voted for these laws, i also informed the king about the fact that these medicine are poison before the law took effect. Confirmation by the greffe and director of the kings cabinet are provided with this email (1).

With the laws that give instructions to “treat” certain groups in the population and the medicine used in that treatement turns out to be poison, the kingdom of the netherlands is, with the signature of the king, committing the following crimes mentioned in article 6:

| *   Killing members of the group
| *   Causing serious bodily or mental harm to members of the group
| *   .
| *   Imposing measures intended to prevent births within the group
| *   .

Since the members of the chamber and the king were aware that these medicine are poison at the time they voted for this law and the day the Wfz law took effect (1-1-2019) i ask the prosecutor to prosecute the king and members of the chamber for three genocide crimes mentioned in article 6 on the note that this does not entail etnicity or nationality but on general groups in the population.

I hope you can stop the above mentioned crimes the king of the netherlands and his government are doing."""

def register(k):
    k.addcmd(req)

def req(event):
    event.reply(__doc__)
