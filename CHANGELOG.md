# Changelog (dziennik zmian):

## [0.10.0] - 2023-01-03

### Dodano
- Dodatkowy tryb wyświetlania otworów B - wyświetlane są otwory z przestrzennego zakresu widoku mapy.
- Narzędzie mapowe do ręcznego zaznaczania otworu B z poziomu mapy.
- Podpowiedzi tekstowe (tooltip) dla przycisków - pojawiają się po zatrzmaniu kursora nad danym przyciskiem.

### Zmieniono
- Zwiększono rozdzielczość ikonki wtyczki.
- Uporządkowano elementy interfejsu użytkownika.

### Poprawiono
- Umożliwiono analizę baz danych, które są całkowicie pozbawione wartości parametrów: Z, Głęb., Rok.
- Poprawiono błędy związane z interpretowaniem parametrów o wartości liczbowej 0 jako fałsz (False).
- Opróżnienie aktywnej kategorii z otworów A powoduje automatyczne przejście do innej niepustej kategorii.
- Uniemożliwiono nadawanie lokalizacji współrzędnych XY wg otworu B, jeśli otwór A nie jest połączony z otworem B.

## [0.9.8] - 2022-11-28

### Zmieniono
- Zmodyfikowano działanie funkcji sprawdzającej, czy niezbędne dla działania wtyczki biblioteki python są zainstalowane. W razie stwierdzenia braku wymaganej biblioteki (bądź zainstalowanej zbyt "starej" wersji), jest ona instalowana z pliku .whl pobieranego z repozytorium 'http://dszrek.github.io/libs/'. Konieczność instalowania bibliotek z udostępnionych plików wynika z blokowania przez proxy sieci PIG-PIB domyślnego instalatora sieciowego "pip".

### Poprawiono
- Zapewniono zgodność działania wtyczki na wersjach QGIS opartych o Python 3.9 (wersje QGIS nowsze niż 3.16.6). Niedziałająca w wersji Python 3.9 biblioteka 'pyarrow' została zastąpiona przez 'fastparquet'.

## [0.9.7] - 2021-07-07

### Dodano
- Umożliwienie importu i analizy otworów bez współrzędnych XY wymusiło stworzenie funkcji odpowiedzialnej za automatyczny dobór dostępnych kategorii lokalizacji, np. jeżeli brak jest współrzędnych otworu A, to nie można ustawić lokalizacji typu "A".
- Wprowadzono nową kategorię lokalizacji - "?", która oznacza brak możliwości ustalenia prawidłowej lokalizacji otworu.

### Zmieniono
- Punkt "C" jest uwzględniany przy ustalaniu zakresu widoku mapy.

### Poprawiono
- Po wczytaniu uwcześnie zapisanego pliku projektowego i uruchomieniu wtyczki, etykiety otworów są już wyświetlane na mapie.
- Po wciśnięciu przycisku "USTAL POŁĄCZENIE" (zatwierdzenie zastąpienia prawidłowego otworu B bez modyfikacji kategorii otworu A) nie dochodzi do zmiany aktualnie zaznaczonego otworu A.

## [0.9.6] - 2021-07-05

### Dodano
- Możliwość importu i analizy otworów bez współrzędnych XY.

### Poprawiono
- Sortowanie po pierwszym kliknięciu na nagłówku kolumny w tabelach A lub B jest ustawione na malejące we wszystkich przypadkach.

## [0.9.5] - 2021-07-02

### Zmieniono
- Zmodyfikowano metodę oceny dopasowania otworów w analizie pełnej. Wykorzystany w niej algorytm k najbliższych sąsiadów (k Nearest Neighbors) liczony jest teraz nie z 5 parametrów, lecz ze średniej i mediany tych parametrów. To rozwiązanie promuje prawidłowe otwory z bazy B, jeśli nie wszystkie paramatry są dostępne (np. brak współrzędnych, danych o głębokości itp.).

## [0.9.4] - 2021-07-01

### Dodano
- Możliwość sortowania tabeli z otworami B.

### Zmieniono
- Po pierwszym kliknięciu na nagłówku kolumny w tabelach z otworami A lub B dane sortują się malejąco (poprzednio domyślnie sortowały się rosnąco).
- Przycisk "PEŁNA ANALIZA" do tej pory służył w celu przeprowadzenia analizy dopasowania otworu A ze wszystkimi otworami z bazy B. Po przeprowadzeniu analizy zwracana była lista 10. najlepiej dopasowanych otworów B. Okazało się, że w niektórych przypadkach limit 10 otworów był zbyt rygorystyczny i otwór, który powinien zostać przypasowany nie pojawiał się na liście. W tej wersji wtyczki, po przeprowadzonej pełnej analizie i wyłonieniu 10. najlepszych otworów (użycie przycisku "PEŁNA ANALIZA [10]") istnieje możliwość powtórzenia analizy ("PEŁNA ANALIZA [100]"), po której zwrócone zostanie 100 otworów (otwór A otrzymuje wtedy status przeanalizowania równy "3"). Do analizy tak licznej ilości otworów B zaleca się używanie sortowania tabeli otworów B po poszczególnych kolumnach.

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
- Parametr N uzyskuje wartość 0.0, jeśli w otworze A lub B brak jest nazwy (pusta wartość w nazwie otworu powodowała błąd analizy wstępnej).

## [0.9.1] - 2021-05-10

### Zmieniono
- Fazę 3 analizy wstępnej oparto na wartościach pojedynczych parametrów, zamiast na kombinacjach uśrednionych wartości par parametrów.

### Poprawiono
- Eksport połączonych otworów do pliku .csv - do kolumny 'Y' wpisywana jest poprawna współrzędna.
