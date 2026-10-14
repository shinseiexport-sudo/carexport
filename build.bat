@echo off
rem ============================================================
rem  サイトを再生成します: img/ (元画像) -> web/ (表示用画像) -> site/ (HTML一式)
rem  使い方: build.bat をダブルクリック、またはコマンドプロンプトで build.bat
rem  必要: Python 3 と Pillow (pip install pillow)
rem ============================================================
setlocal
cd /d "%~dp0"

echo [1/2] 表示用の画像を書き出します (img/ -^> web/)
python make_images.py
if errorlevel 1 goto :err

echo.
echo [2/2] HTMLを生成します (build/ -^> site/)
python build/site.py
if errorlevel 1 goto :err

echo.
echo 完了: site/ に出力しました
pause
exit /b 0

:err
echo.
echo エラーが発生しました。上のメッセージを確認してください。
pause
exit /b 1
