CD %~dp0
FOR %%A IN (%*) DO (
SET USEFILE=%%A
python cadreur_batch.py %%A
)
pause
