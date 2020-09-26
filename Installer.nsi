/* NSIS Installer File for Angel */


/* File metadata such as name and license */
Name "Angel"
OutFile "Installer.exe"
Caption "A Reddit Client"
LicenseData LICENSE.txt
LicenseBkColor 0xFAFAFA
InstallButtonText "Next >"
ShowInstDetails show
InstallDir $APPDATA\Angel
XPStyle on
!include "x64.nsh"

/* Disable x64 redirection to System instead of System32 */

Section 'disableredirect'
  ${DisableX64FSRedirection}
SectionEnd
/* License page - GPLv2 */
Page License

Page instfiles
  Caption ': Angel for Reddit Installation'
  CompletedText "Angel for Reddit Installation Complete"
  Section 'files'
    CreateDirectory "$SMPROGRAMS\Angel"
    CreateShortCut "$SMPROGRAMS\Angel\Angel.lnk" "$INSTDIR\Angel.exe" "" "$INSTDIR\angel.ico"
    SetOutPath "$APPDATA\Angel"
    File Angel.exe
    File angel.desktop
    File angel.ico
    File angel.png
    File default.png
    File downvote.png
    File imagelink.png
    File link.png
    File loading.gif
    File mask.png
    File redditwhite.svg
    File reddit.png
    File text.png
    File upvote.png
    File python3.dll
    File python38.dll
    File vcruntime140.dll
    File video-yt.png
    File video-mp4.png
    File api-ms-win-crt-heap-l1-1-0.dll
    File api-ms-win-crt-locale-l1-1-0.dll
    File api-ms-win-crt-runtime-l1-1-0.dll
    File api-ms-win-crt-stdio-l1-1-0.dll
    File /r lib
SectionEnd
