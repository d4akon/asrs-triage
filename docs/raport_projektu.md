# ASRS triage: automatyczna klasyfikacja i analiza trendów raportów bezpieczeństwa lotniczego

Prototyp (proof of concept) do pracy magisterskiej. Repozytorium: `asrs-triage`.

## 1. Co robi projekt

System ASRS (Aviation Safety Reporting System) prowadzony przez NASA zbiera dobrowolne zgłoszenia od pilotów, kontrolerów, mechaników i personelu pokładowego. Każdy raport zawiera narrację w formie swobodnego tekstu, a analitycy ASRS ręcznie przypisują mu etykiety. Projekt:

1. **Klasyfikuje** narrację automatycznie, przewidując etykiety **Anomaly** analityków (może pasować kilka naraz, 53 etykiety) oraz **Primary Problem** (jedna przyczyna z 18).
2. **Porównuje** prosty model statystyczny (TF-IDF z liniowym SVM) z dostrojonym transformerem (DeBERTa-v3 z LoRA) przy identycznej ewaluacji.
3. **Analizuje trendy** w latach 2018-2021: jak często w kolejnych miesiącach pojawia się każda etykieta i każdy automatycznie znaleziony temat oraz kiedy częstość się zmienia.
4. **Udostępnia** model bazowy w lokalnej aplikacji demonstracyjnej (back end FastAPI, front end Angular).

Wszystkie stwierdzenia dotyczą **raportów otrzymanych przez ASRS**, a nie zdarzeń, które faktycznie miały miejsce. System jest dobrowolny i niezweryfikowany, więc zmiany częstości mogą odzwierciedlać zachowania zgłaszających.

## 2. Dane

- Źródło: eksporty CSV z ASRS Database Online. Portal ogranicza eksport do 5 000 rekordów, więc dane pobrano w przedziałach półrocznych i połączono (`scripts/load_raw.py`).
- Rozmiar po czyszczeniu: **21 633 raporty, od stycznia 2018 do grudnia 2021** (około 450 miesięcznie).
- Wejście modeli: wyłącznie tekst narracji (obie narracje zgłaszających połączone). Pola **Synopsis** i **Callback** pisane przez analityka nie są nigdy używane, ponieważ ten sam analityk przypisuje etykiety i pola te zdradzałyby odpowiedź (wyciek etykiet).
- Czyszczenie (`scripts/clean.py`): znacznik `ZZZ` (zanonimizowane nazwy i miejsca) zamieniany jest na `[ANON]`; usuwane są raporty bez tekstu, etykiet lub daty oraz miesiące z mniej niż 20 raportami.
- **Podział chronologiczny** po miesiącach (`scripts/split.py`): pierwsze 70% raportów do uczenia (15 178), kolejne 15% do walidacji (3 428), ostatnie 15% do testu (3 027). Model jest zawsze testowany na raportach nowszych niż te, na których się uczył, tak jak byłby używany w praktyce. Podział losowy pozwoliłby mu uczyć się z "przyszłości".
- Etykiety Anomaly z mniej niż 30 przykładami w zbiorze uczącym są pomijane, zostaje 53.

## 3. Metody

**Model bazowy** (`scripts/baseline.py`): cechy TF-IDF (słowa i bigramy, dopasowane tylko na zbiorze uczącym) oraz liniowy SVM ze zrównoważonymi wagami klas; dla wieloetykietowego zadania Anomaly podejście one-vs-rest.

**Transformer** (`scripts/train_transformer.py`): DeBERTa-v3-base dostrojony metodą LoRA (trenowane są małe macierze adapterów zamiast całego modelu), jeden wspólny enkoder z dwiema głowicami (Anomaly z ważoną stratą binarną, Primary Problem z ważoną entropią krzyżową). Uczenie na darmowym GPU Kaggle przez 6 epok; próg decyzyjny dla Anomaly dobierany na zbiorze walidacyjnym.

**Skracanie tekstu.** Transformer czyta najwyżej 512 tokenów, a około 24% raportów testowych jest dłuższych. Przebieg 7 zachowywał pierwsze 510 tokenów (ucinał koniec). Przebieg 8 zachowuje **pierwsze 128 i ostatnie 382 tokeny** ("head+tail"), ponieważ koniec narracji często opisuje, co się stało.

**Ewaluacja** (`scripts/evaluate.py`): jedna wspólna funkcja dla obu modeli. Główną miarą jest **macro-F1**, czyli średnia z wyników dla poszczególnych etykiet, dzięki czemu rzadkie etykiety liczą się tak samo jak częste; raportowane są też micro-F1, strata Hamminga i F1 dla każdej etykiety.

## 4. Wyniki

Zbiór testowy, 3 027 raportów, podział chronologiczny:

| Zadanie | Miara | TF-IDF + SVM | DeBERTa-v3 + LoRA (head) | DeBERTa-v3 + LoRA (head+tail) |
|---|---|---|---|---|
| Anomaly | macro-F1 | 0,401 | 0,376 | 0,396 |
| Anomaly | micro-F1 | 0,603 | 0,522 | 0,513 |
| Primary Problem | macro-F1 | 0,305 | 0,296 | 0,343 |
| Primary Problem | micro-F1 | 0,639 | 0,602 | 0,626 |

- **Prosty model bazowy trudno pobić na tych danych.** Transformer wyraźnie przegrywał przy pierwszym sposobie skracania (przebieg 7).
- **Skracanie head+tail pomogło** (+0,020 macro-F1 dla Anomaly, +0,047 macro-F1 dla Primary Problem): model przewyższa teraz bazowy pod względem macro-F1 dla Primary Problem, mniej więcej remisuje dla Anomaly i nadal ustępuje w micro-F1. To pojedyncze przebiegi z jednym ziarnem losowym; różnice poniżej około 0,02 nie są potwierdzone.
- Przy stałym progu 0,5 model head+tail osiąga 0,425 macro-F1 dla Anomaly na zbiorze testowym. Podaję to dla przejrzystości, ale nie jako wynik główny, ponieważ próg nie został wybrany z góry (próg dobrany na walidacji daje 0,396).
- **Więcej danych bardzo pomogło:** na samym roku 2019 macro-F1 transformera dla Primary Problem wynosiło 0,216; na latach 2018-2021 jest to 0,296 (head) i 0,343 (head+tail).

**Analiza błędów** (`results/error_analysis.md`, przebieg 7): poprawne przypisanie wszystkich etykiet raportu zdarza się w 7,5% raportów testowych (transformer) i 12,4% (model bazowy); transformer przewiduje mniej etykiet na raport niż analitycy (2,6 wobec 3,1); trafność spada wraz z długością raportu; główne pomyłki dotyczące przyczyny to Procedure kontra Human Factors. Wiele przejrzanych błędów wygląda na wybór etykiet przez analityka (np. ogólne etykiety, takie jak "Published Material / Policy", dodane do raportów, które są poza tym jednoznaczne), a nie na błąd modelu.

**Kalibracja** (`results/calibration.json`): surowe wyniki SVM nie są prawdopodobieństwami. Skalowanie Platta dopasowane na zbiorze walidacyjnym obniża oczekiwany błąd kalibracji (ECE) na zbiorze testowym z 0,22 do 0,016 dla Anomaly i z 0,50 do 0,019 dla Primary Problem.

## 5. Analiza trendów

Każdy raport został oceniony przez model, który go nie widział (5-krotna walidacja krzyżowa, losowe podziały), a następnie policzony miesięcznie według etykiety przewidzianej i, dla porównania, rzeczywistej. Punkty zmiany wyznaczono metodą PELT, tematy za pomocą BERTopic (embeddingi zdań, UMAP, HDBSCAN, 25 tematów, bez użycia etykiet).

![Miesięczne udziały etykiet z wykrytymi punktami zmiany](figures/top_label_trends.png)

- **Przewidywania dobrze odtwarzają prawdziwe trendy miesięczne dla etykiet specyficznych** (korelacja 0,89-0,99 dla ATC Issue, CFTT/CFIT, NMAC, Smoke/Fire) **i słabo dla ogólnych** (Clearance 0,21, FAR 0,42), gdzie analitycy etykietują niespójnie. Wnioski o trendach ograniczam do pierwszej grupy.
- **COVID-19 jest widoczny.** Liczba raportów spada do 244 w kwietniu 2020 i rośnie do 617 w lipcu 2020. Nienadzorowany temat o maskach (`mask, passenger, wearing, face, policy`) nie występuje przed lutym 2020, a w sierpniu 2020 osiąga szczyt 14,7% raportów. Żadna etykieta ASRS nie opisuje tego motywu.
- **Widoczna jest zmiana w sposobie etykietowania przez analityków.** Liczba etykiet na raport rośnie z około 2,5 do około 3,3 od początku 2021, głównie za sprawą FAR, Published Material, Clearance i Equipment Problem Critical. Prawdopodobnie odzwierciedla to praktykę analityków, a nie to, co zgłaszano, więc udziały etykiet sprzed i po tej zmianie nie są wprost porównywalne. Nie znalazłem dokumentacji tej zmiany; to hipoteza.
- Kilka skoków (ATC Issue i Weather w kwietniu 2019, Equipment Less Severe w lutym 2020, NMAC w maju 2021) nie ma przyczyny, którą udało mi się zidentyfikować.

**Kontrola wycieku danych.** Podział na zbiór uczący, walidacyjny i testowy jest chronologiczny (uczący 2018-01 do 2020-08, walidacyjny 2020-09 do 2021-04, testowy 2021-05 do 2021-12), bez wspólnych miesięcy, numerów raportów (ACN) ani identycznych tekstów. Ponieważ wykresy trendów korzystają z losowych podziałów, porównanie powtórzono ściśle w czasie (`scripts/leakage_check.py`): mediana korelacji 0,68 wobec 0,67 i około 30% większe błędy miesięcznych udziałów. Analiza tematów w ogóle nie używa etykiet.

![Tematy z największą zmianą](figures/topic_trends.png)

## 6. Aplikacja demonstracyjna

Interfejs aplikacji jest w języku angielskim.

![Klasyfikacja raportu](screenshots/01-classify.png)

Po wklejeniu raportu (lub użyciu przycisku z przykładem) aplikacja pokazuje:

- najbardziej prawdopodobne **typy zdarzeń** oraz **przyczynę** jako skalibrowane prawdopodobieństwa;
- **"because of"**: słowa z tekstu, które podniosły wynik danej etykiety (na podstawie wag modelu liniowego);
- **trzy najbardziej podobne wcześniejsze raporty** spośród 21 633, wraz z ich etykietami.

Strona **Trends** pokazuje miesięczny udział dowolnej etykiety (etykiety analityków obok przewidywań modelu, wykryte punkty zmiany, zaznaczony okres COVID), tematy nienadzorowane, liczbę raportów oraz liczbę etykiet na raport.

![Strona trendów](screenshots/02-trends-labels.png)

![Widok tematów z tematem o maskach](screenshots/03-trends-topics.png)

Uwagi: przyczyna pokazana jako pierwsza jest decyzją samego modelu, która może mieć niższy procent niż inna przyczyna, ponieważ skalibrowane prawdopodobieństwa faworyzują klasy częste (użycie ich do decyzji obniżyłoby macro-F1 dla przyczyny z 0,305 do 0,266). Demo używa modelu bazowego, który jest szybki i działa bez GPU.

## 7. Jak to jest zbudowane

| Część | Technologia |
|---|---|
| Dane i model bazowy | Python 3.12, pandas, scikit-learn |
| Transformer | PyTorch, Hugging Face Transformers, PEFT (LoRA), uczenie na GPU Kaggle |
| Trendy i tematy | ruptures (punkty zmiany), BERTopic, sentence-transformers |
| API | FastAPI (`/predict`, `/trends/labels`, `/trends/topics`) |
| Front end | Angular 22, komponenty standalone, sygnały, własne wykresy SVG |
| Testy | Vitest (5 testów front endu) |

Struktura repozytorium i instrukcja uruchomienia są w `README.md`. W skrócie:

```bash
pip install -r requirements.txt
python scripts/load_raw.py && python scripts/clean.py && python scripts/split.py
python scripts/baseline.py
python scripts/trends.py && python scripts/topics.py
python scripts/export_baseline.py
./run_demo.sh        # API na :8000, aplikacja na :4200
```

Przebieg prac jest zapisany w historii Gita (komunikaty w konwencji Conventional Commits). Decyzje projektowe (podział chronologiczny, wykluczenie pola Synopsis, protokół porównania) i interpretacja wyników są opisane powyżej.

## 8. Ograniczenia

- Tylko cztery lata i około 21,6 tys. raportów (plan zakładał 30 tys. lub więcej); cztery lata nie pozwalają odróżnić sezonowości od trendu.
- Pojedyncze przebiegi uczenia, jedno ziarno losowe; dotąd jedna ablacja (skracanie tekstu).
- Przewidywania w analizie trendów pochodzą z walidacji krzyżowej z losowymi podziałami. Sprawdzenie ściśle w czasie (uczenie na wcześniejszych latach, predykcja 2019, 2020, 2021) dało takie samo odwzorowanie trendów (mediana korelacji 0,68 wobec 0,67), ale o około 30% większe błędy miesięcznych udziałów, więc poziomy są mniej dokładne, niż sugerują wykresy; kształty trendów nie wynikają z wycieku danych.
- Zmiana w etykietowaniu w 2021 ogranicza porównywanie udziałów etykiet ponad nią.
- Kalibracja w demie jest dopasowana na jednym podziale z jednego okresu.

## 9. Dalsze kroki

- Ulepszenie transformera: kolejne ablacje (maksymalna długość, learning rate, wagi klas), model o dłuższym kontekście, kilka ziaren losowych.
- Więcej danych (od 2022), aby osiągnąć planowany rozmiar i sprawdzić, czy zmiana w etykietowaniu się utrzymuje.
- Możliwe rozszerzenie, jeśli starczy czasu: transkrypcja rozmów radiowych kontroli ruchu lotniczego i klasyfikacja transkryptów wytrenowanym modelem.
