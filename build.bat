@echo off
pyinstaller --onefile ^
  --add-data "files/*;files/" ^
  --add-data ".env;." ^
  --hidden-import=azure.cognitiveservices.speech ^
  --add-binary "d:/projects/deleteme/.venv/Lib/site-packages/azure/cognitiveservices/speech/Microsoft.CognitiveServices.Speech.core.dll;azure/cognitiveservices/speech" ^
  --add-binary "d:/projects/deleteme/.venv/Lib/site-packages/azure/cognitiveservices/speech/Microsoft.CognitiveServices.Speech.extension.audio.sys.dll;azure/cognitiveservices/speech" ^
  --add-binary "d:/projects/deleteme/.venv/Lib/site-packages/azure/cognitiveservices/speech/Microsoft.CognitiveServices.Speech.extension.codec.dll;azure/cognitiveservices/speech" ^
  --add-binary "d:/projects/deleteme/.venv/Lib/site-packages/azure/cognitiveservices/speech/Microsoft.CognitiveServices.Speech.extension.kws.dll;azure/cognitiveservices/speech" ^
  --add-binary "d:/projects/deleteme/.venv/Lib/site-packages/azure/cognitiveservices/speech/Microsoft.CognitiveServices.Speech.extension.lu.dll;azure/cognitiveservices/speech" ^
  --exclude-module=vosk ^
  leia.py

echo Build complete! Check the dist directory for leia.exe
pause