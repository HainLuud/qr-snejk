# QR-Snek

## Olulisemad asjad

### Vaja implementeerida
Ussi klassi sees on kaks funktsiooni, mis peavad ütlema, kuhu suunas uss järgmisena liigub.
- aiMove() - Hain - siia sisse tuleb kirjutada ai loogika, mis peab tagastama ühe suuna (UP, DOWN, LEFT, RIGHT).
- qrMove() - Jürgen - siia sisse tuleb kirjutada qr loogika, mis peab tagastama ühe suuna (UP, DOWN, LEFT, RIGHT).

Katsetamise mõttes tagastavad praegu mõlemad funktsioonid suvalise käigu, mis ei sõida ussile endale sisse.

### Globaalsed muutujad
- BOARD - mängulaud (2d-list), iga elemendi väärtus on kas 
  - None - Ruut on tühi
  - 0 - Ruudul on toit
  - {number} - ussi id, mille keha on sellel ruudul
- FOOD_LOC - toidu koordinaadid kujul (x,y)
- UP, DOWN, LEFT, RIGHT - suunad, mida on võimalik ussile järmise käigu jaoks ette anda. (Need on tuple kujul (x_muutus, y_muutus))
- SNAKES - List mängus olevate ussi objektidega

### Uss
Ussi jaoks on olemas klass Snake, selle sees on
muutujad:
- id - ussi id, mis pannakse mängulauale (nt 1, 2, ...).
- position - list ussi keha koordinaatide tuple-test (nt [(0,0), (0,1), (0,2)]) kus kõige viimane element on ussi pea.
- lastDirection - viimase sammu liikumise suund.

funktsioonid:
- moveDecider() - mäng kutsub seda funktsiooni, kui on vaja ussi liigutada. Funktsioon peab tagastama ühe liikumissuuna (UP, DOWN, LEFT, RIGHT). Vastavalt ussi tüübile määratakse see konstruktoris aliaseks kas aiMove() või qrMove() funktsioonile.

## Vähem oluline
Muutujad:
- GAME_SPEED - mängu kiirus(fps)
- BOARD_WIDTH - ruudustiku tulpade arv
- BOARD_HEIGHT - ruudustiku ridade arv
- BLOCK_SIZE - ühe ruudu külg pikslites

Funktsioonid:
- main() - mängu setup ja loop. Siin toimub ka usside loomine. Arendamise ajaks võite ühe ussidest välja kommenteerida.
