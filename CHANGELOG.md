# Changelog (dziennik zmian):

## [0.9.3] - 2021-06-08 (hotfix)

### Poprawiono
- Błąd związany z wyświetlaniem na mapie otworów, których wartosć ID nie jest numeryczna (złożona z samych cyfr).
- Błąd uniemożliwiający ustanowienie lokalizacji typu C.

## [0.9.2] - 2021-05-20

### Dodano
- Uruchamianie wtyczki z otwartym "własnym" plikiem projektowym - możliwość korzystania z dodatkowych warstw danych. Dodatkowe warstwy nie są usuwane z projektu podczas uruchamiania wtyczki.
- Automatyczne wyłączanie wtyczki po stwierdzeniu usunięcia/zmiany warstwy niezbędnej dla funkcjonowania wtyczki (którakolwiek z warstw z grupy "WellMatch").

### Zmieniono
- Przyciski "Utwórz projekt" i "Wczytaj projekt" zostały zastępione przez jeden przycisk "Utwórz / wczytaj projekt", który spełnia funkcje obu poprzedników.
- Na początku fazy 4 analizy wstępnej algorytm buduje tzw. macierz połączeń ustalonych. Czas trwania tej pętli przeważnie wynosi kilka sekund, ale dla niektórych zespołów danych może się wydłużyć nawet do kilku minut. Dotychczas ta "podfaza" nie była uwzględniana w interfejsie wtyczki i jeśli trwała długo, to można było odnieść wrażenie, że nastąpił błąd działania analizy (wtyczka przez długi czas nie odświeżała postępu analizy). W tej wersji wyświetlane są informacje dotyczące tworzenia macierzy połączeń ustalonych.

### Poprawiono
- Zapobieganie dodawania '.0' do wartości kolumn ID i NAZWA, jeśli wartość złożona jest z samych cyfr (np. 12345 zamienione na 12345.0). Wtyczka zamiast traktować wartości jako tekst, traktowała je jako liczby i automatycznie konwertowała do typu liczb zmiennoprzecinkowych.
- Wyeliminowano błędy dopasowania rozmytego (fuzzy matchingu) związane z pustymi wartościami w kolumnie NAZWA.
- Analiza wstępna nie zawiesza się już po 3 fazie z błędem typu "ValueError: Shape of passed values is (2463, 2), indices imply (2399, 2))". Błąd pojawiał się przy wykonywaniu analizy, po przejściu do kolejnego projektu bez wyłączania wtyczki. Wtyczka "pamiętała" dane z poprzedniego projektu, co było powodem występowania błędów w kolejnej analizie.
- Można zacząć importowanie danych od bazy B (klikając na przycisk "Importuj bazę B"). Wcześniej import bazy B przed zaimportowaniem bazy A powodował wystąpienie błędu, który uniemożliwiał przeprowadzenie analizy wstępnej.
- Poprawiono wiele drobnych błędów wpływających na stabilność działania analizy wstępnej.

## [0.9.11] - 2021-05-10 (hotfix 1)

### Poprawiono
- Parametr N uzyskuje wartość 0.0, jeśli w otworze A lub B brak jest nazwy (pusta wartość w nazwie otworu powodowała błąd analizy wstępnej).

## [0.9.1] - 2021-05-10

### Zmieniono
- Fazę 3 analizy wstępnej oparto na wartościach pojedynczych parametrów, zamiast na kombinacjach uśrednionych wartości par parametrów.

### Poprawiono
- Eksport połączonych otworów do pliku .csv - do kolumny 'Y' wpisywana jest poprawna współrzędna.
