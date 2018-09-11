CD %~dp0
FOR %%A IN (%*) DO (
SET USEFILE=%%A
java -jar ../jar/processing-py.jar cadreur_batch.pyde
)
pause
