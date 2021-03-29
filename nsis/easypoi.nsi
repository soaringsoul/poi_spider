; 该脚本使用 HM VNISEdit 脚本编辑器向导产生

; 安装程序初始定义常量
!define PRODUCT_NAME "EasyPoi_Win64安装程序V1.0.exe"
!define PRODUCT_VERSION "1.0"
!define PRODUCT_PUBLISHER "人文互联网"
!define PRODUCT_WEB_SITE "https://mp.weixin.qq.com/s/JRZNlNYbW3CYO9fDDZt88w"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\easypoi.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor lzma

; ------ MUI 现代界面定义 (1.67 版本以上兼容) ------
!include "MUI.nsh"

; MUI 预定义常量
!define MUI_ABORTWARNING
!define MUI_ICON "..\favicon.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; 欢迎页面
!insertmacro MUI_PAGE_WELCOME
; 安装目录选择页面
!insertmacro MUI_PAGE_DIRECTORY
; 安装过程页面
!insertmacro MUI_PAGE_INSTFILES
; 安装完成页面
!define MUI_FINISHPAGE_RUN "$INSTDIR\easypoi.exe"
!insertmacro MUI_PAGE_FINISH

; 安装卸载过程页面
!insertmacro MUI_UNPAGE_INSTFILES

; 安装界面包含的语言设置
!insertmacro MUI_LANGUAGE "SimpChinese"

; 安装预释放文件
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS
; ------ MUI 现代界面定义结束 ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "百度地图POI采集工具windows64位安装程序.exe"
InstallDir "$PROGRAMFILES\百度地图POI采集工具"
InstallDirRegKey HKLM "${PRODUCT_UNINST_KEY}" "UninstallString"
ShowInstDetails show
ShowUnInstDetails show

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  File "..\dist\easypoi\easypoi.exe"
  CreateDirectory "$SMPROGRAMS\百度地图POI采集工具"
  CreateShortCut "$SMPROGRAMS\百度地图POI采集工具\百度地图POI采集工具.lnk" "$INSTDIR\easypoi.exe"
  CreateShortCut "$DESKTOP\百度地图POI采集工具.lnk" "$INSTDIR\easypoi.exe"
  File /r "..\dist\easypoi\*.*"
SectionEnd

Section -AdditionalIcons
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\百度地图POI采集工具\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\百度地图POI采集工具\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\easypoi.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\easypoi.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

/******************************
 *  以下是安装程序的卸载部分  *
 ******************************/

Section Uninstall
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\easypoi.exe"

  Delete "$SMPROGRAMS\百度地图POI采集工具\Uninstall.lnk"
  Delete "$SMPROGRAMS\百度地图POI采集工具\Website.lnk"
  Delete "$DESKTOP\百度地图POI采集工具.lnk"
  Delete "$SMPROGRAMS\百度地图POI采集工具\百度地图POI采集工具.lnk"

  RMDir "$SMPROGRAMS\百度地图POI采集工具"

  RMDir /r "$INSTDIR\zope"
  RMDir /r "$INSTDIR\themes"
  RMDir /r "$INSTDIR\sqlalchemy"
  RMDir /r "$INSTDIR\shapely"
  RMDir /r "$INSTDIR\scrapy"
  RMDir /r "$INSTDIR\result"
  RMDir /r "$INSTDIR\pytz"
  RMDir /r "$INSTDIR\PyQt5"
  RMDir /r "$INSTDIR\poi_spider"
  RMDir /r "$INSTDIR\pandas"
  RMDir /r "$INSTDIR\numpy"
  RMDir /r "$INSTDIR\lxml"
  RMDir /r "$INSTDIR\Include"
  RMDir /r "$INSTDIR\data"
  RMDir /r "$INSTDIR\cryptography-3.4.5-py3.7.egg-info"
  RMDir /r "$INSTDIR\cryptography"
  RMDir /r "$INSTDIR\certifi"

  RMDir "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd

#-- 根据 NSIS 脚本编辑规则，所有 Function 区段必须放置在 Section 区段之后编写，以避免安装程序出现未可预知的问题。--#

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "您确实要完全移除 $(^Name) ，及其所有的组件？" IDYES +2
  Abort
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) 已成功地从您的计算机移除。"
FunctionEnd
