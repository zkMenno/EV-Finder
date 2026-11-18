# Model-level EU coverage gaps after T-136 (WS3 branch t-136-missing-models @ 7cd4a36)

Measured 2026-11-18 by WS1 with `ev variants` model coverage (PR #127): EEA EU-wide BEV registrations 2010–2025 (CC BY 4.0, counts only), 9,083,321 with a model name. Each make + name goes through the seed matcher with EEA's own aliases, as `ev release` does.

- main (99 models): 86.7 %
- WS3 branch (135 models): **95.7 %**

Next biggest unplaced names. `model not in seed` under a make we have is often a missing EEA alias for a model we already have (e.g. SMART FORTWO / ELECTRIC DRIVE, MG ZS EXCLUSIVE EV, KIA NIRO 4 EV, HYUNDAI KONA PREMIUM EV); `make not in seed` is a new make. Vans and non-BEV oddities (Prius, Auris hybrid, Proace, Vivaro, Jumpy) are EEA reporting noise or out of scope: skip them.

| Registrations | Cumulative % | Make | EEA name | Reason |
|---:|---:|---|---|---|
| 15,128 | 95.9 | SEAT | MII | make not in seed |
| 6,361 | 96.0 | ALPINE | A290 | make not in seed |
| 5,974 | 96.1 | SMART | FORTWO | model not in seed |
| 5,937 | 96.1 | MERCEDES-BENZ | EVITO TOURER | model not in seed |
| 5,739 | 96.2 | NISSAN | NISSAN E-NV200 | model not in seed |
| 5,663 | 96.2 | OPEL | GRANDLAND | model not in seed |
| 5,615 | 96.3 | HONDA | E:NY1 | model not in seed |
| 5,395 | 96.4 | SMART | ELECTRIC DRIVE | model not in seed |
| 5,333 | 96.4 | MG | ZS EXCLUSIVE EV | model not in seed |
| 5,239 | 96.5 | ABARTH | 500 | make not in seed |
| 5,115 | 96.5 | SUBARU | SOLTERRA | model not in seed |
| 5,089 | 96.6 | LEXUS | LEXUS UX300E | make not in seed |
| 4,867 | 96.6 | POLESTAR | POLESTAR 3 | model not in seed |
| 4,863 | 96.7 | KIA | NIRO 4 EV | model not in seed |
| 4,720 | 96.8 | ALFA ROMEO | ALFA ROMEO JUNIOR | make not in seed |
| 4,686 | 96.8 | TESLA | MODEL | model not in seed |
| 4,353 | 96.9 | OPEL | COMBO-E LIFE | model not in seed |
| 4,340 | 96.9 | TOYOTA | PROACE | model not in seed |
| 4,270 | 96.9 | AIWAYS | U5 | make not in seed |
| 4,270 | 97.0 | GREAT WALL MOTOR COMPANY LIMITED | ORA FUNKY CAT | make not in seed |
| 3,876 | 97.0 | BYD | SEALION | model not in seed |
| 3,700 | 97.1 | LEXUS | LEXUS RZ450E | make not in seed |
| 3,419 | 97.1 | TOYOTA | PRIUS | model not in seed |
| 3,289 | 97.2 | RENAULT | KANGOO E-TECH ELECTRIC | model not in seed |
| 3,228 | 97.2 | LEAPMOTOR | C10 | model not in seed |
| 3,087 | 97.2 | SMART | #5 | model not in seed |
| 3,073 | 97.3 | BLUECAR | BLUECAR | make not in seed |
| 3,049 | 97.3 | RENAULT | RENAULT 5 | model not in seed |
| 2,947 | 97.3 | LEAPMOTOR | B10 | model not in seed |
| 2,923 | 97.4 | HYUNDAI | KONA PREMIUM SE EV AUTO | model not in seed |
| 2,912 | 97.4 | SMART | FORTWO COUPE ED | model not in seed |
| 2,853 | 97.4 | GREAT WALL MOTOR CO. LTD. | ORA FUNKY CAT | make not in seed |
| 2,836 | 97.4 | TOYOTA | PROACE CITY VERSO ELECTRIC | model not in seed |
| 2,731 | 97.5 | OPEL | VIVARO | model not in seed |
| 2,543 | 97.5 | MAXUS | MAXUS EUNIQ 6 | make not in seed |
| 2,520 | 97.5 | CITROEN | JUMPY | model not in seed |
| 2,490 | 97.6 | BYD | BYD TANG | model not in seed |
| 2,431 | 97.6 | FISKER | OCEAN | make not in seed |
| 2,349 | 97.6 | HYUNDAI | KONA PREMIUM EV AUTO | model not in seed |
| 2,310 | 97.6 | MERCEDES-BENZ | G 580 | model not in seed |
| 2,284 | 97.7 | HYUNDAI | IONIQ PREMIUM EV | model not in seed |
| 2,252 | 97.7 | RENAULT | SCENIC | model not in seed |
| 2,225 | 97.7 | BMW I | SERIE I | model not in seed |
| 2,203 | 97.7 | SMART | FORTWO COUPE ELECTRIC DRI | model not in seed |
| 2,175 | 97.8 | LOTUS | ELETRE | make not in seed |
| 2,168 | 97.8 | BMW | I7 XDRIVE60 | model not in seed |
| 2,129 | 97.8 | NISSAN | E-NV200 | model not in seed |
| 2,083 | 97.8 | MERCEDES-BENZ | B 250 E | model not in seed |
| 2,083 | 97.9 | BYD | HAN | model not in seed |
| 2,002 | 97.9 | DONGFENG | BOX | make not in seed |
| 1,966 | 97.9 | CECOMP | BLUECAR | make not in seed |
| 1,940 | 97.9 | NIO | ET7 | make not in seed |
| 1,917 | 97.9 | PEUGEOT | EXPERT | model not in seed |
| 1,906 | 98.0 | RENAULT | FLUENCE Z.E. | model not in seed |
| 1,882 | 98.0 | TOYOTA | AURIS HYBRID | model not in seed |
| 1,873 | 98.0 | BYD | TANG | model not in seed |
| 1,851 | 98.0 | SMART | FORFOUR ELECTRIC DRIVE | model not in seed |
| 1,842 | 98.0 | SEAT | CUPRA BORN | make not in seed |
| 1,827 | 98.1 | DR | DR EQ1 | make not in seed |
| 1,803 | 98.1 | DFSK | SERES 3 | make not in seed |
| 1,803 | 98.1 | PEUGEOT | N208 | model not in seed |
| 1,787 | 98.1 | NIO | ES8 | make not in seed |
| 1,718 | 98.1 | PEUGEOT | EXPERT TRAVELLER | model not in seed |
| 1,700 | 98.2 | BYD | TANG EV | model not in seed |
| 1,674 | 98.2 | MERCEDES-BENZ | ECITAN TOURER/EQT | model not in seed |
| 1,669 | 98.2 | LANCIA | YPSILON | make not in seed |
| 1,616 | 98.2 | SMART | FORTWO CABRIO ED | model not in seed |
| 1,604 | 98.2 | HYUNDAI | IONIQ PREMIUM SE EV | model not in seed |
| 1,561 | 98.2 | BMW | I7 XDRIVE 60 | model not in seed |
| 1,532 | 98.3 | LEXUS | LEXUS RZ300E | make not in seed |
| 1,467 | 98.3 | FAW | E-HS9 | make not in seed |
| 1,460 | 98.3 | FAW | EHS9 | make not in seed |
| 1,458 | 98.3 | CITROEN | C5 AIRCROSS | model not in seed |
| 1,436 | 98.3 | OPEL | ZAFIRA LIFE | model not in seed |
| 1,425 | 98.3 | MG | MG CYBERSTER | model not in seed |
| 1,421 | 98.4 | SSANGYONG | KORANDO E-MOTION | make not in seed |
| 1,394 | 98.4 | SEAT | BORN 150 KW 58/62 KWH | make not in seed |
| 1,369 | 98.4 | OMODA | OMODA5 EV | make not in seed |
| 1,363 | 98.4 | KIA | EV5 | model not in seed |
| 1,326 | 98.4 | PEUGEOT | TRAVELLER | model not in seed |
