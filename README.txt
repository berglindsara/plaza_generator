PRICER PLAZA – SKJALAFRAMLEIÐSLA
================================

Þetta forrit útbýr SoW og Terms of Use skjöl fyrir nýja viðskiptavini
sjálfkrafa í gegnum vefviðmót.

UPPSETNING (einu sinni)
-----------------------
1. Gakktu úr skugga um að Python 3 sé uppsett á tölvunni þinni.
2. Opnaðu Terminal / Command Prompt í þessari möppu.
3. Settu upp Flask:

   pip install flask

   (eða:  pip3 install flask)

KEYRSLA
-------
Í Terminal / Command Prompt:

   python app.py

   (eða:  python3 app.py)

Opnaðu síðan vafra og farðu á:

   http://localhost:5100

Þar fyllir þú inn upplýsingar og hleður niður tilbúnum Word skjölum.

SKRÁR
-----
app.py                  – Python vefþjónninn (Flask)
template_SoW.docx       – SoW sniðmát
template_Terms.docx     – Terms of Use sniðmát
templates/index.html    – Vefsíðan (formiðs)
generated/              – Tilbúin skjöl eru vistuð hér

ATHUGASEMD
----------
Forritið keyrir eingöngu á þinni eigin tölvu og sendir engar
upplýsingar á netið.
