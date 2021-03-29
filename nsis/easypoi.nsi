; �ýű�ʹ�� HM VNISEdit �ű��༭���򵼲���

; ��װ�����ʼ���峣��
!define PRODUCT_NAME "EasyPoi_Win64��װ����V1.0.exe"
!define PRODUCT_VERSION "1.0"
!define PRODUCT_PUBLISHER "���Ļ�����"
!define PRODUCT_WEB_SITE "https://mp.weixin.qq.com/s/JRZNlNYbW3CYO9fDDZt88w"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\easypoi.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor lzma

; ------ MUI �ִ����涨�� (1.67 �汾���ϼ���) ------
!include "MUI.nsh"

; MUI Ԥ���峣��
!define MUI_ABORTWARNING
!define MUI_ICON "..\favicon.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; ��ӭҳ��
!insertmacro MUI_PAGE_WELCOME
; ��װĿ¼ѡ��ҳ��
!insertmacro MUI_PAGE_DIRECTORY
; ��װ����ҳ��
!insertmacro MUI_PAGE_INSTFILES
; ��װ���ҳ��
!define MUI_FINISHPAGE_RUN "$INSTDIR\easypoi.exe"
!insertmacro MUI_PAGE_FINISH

; ��װж�ع���ҳ��
!insertmacro MUI_UNPAGE_INSTFILES

; ��װ�����������������
!insertmacro MUI_LANGUAGE "SimpChinese"

; ��װԤ�ͷ��ļ�
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS
; ------ MUI �ִ����涨����� ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "�ٶȵ�ͼPOI�ɼ�����windows64λ��װ����.exe"
InstallDir "$PROGRAMFILES\�ٶȵ�ͼPOI�ɼ�����"
InstallDirRegKey HKLM "${PRODUCT_UNINST_KEY}" "UninstallString"
ShowInstDetails show
ShowUnInstDetails show

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  File "..\dist\easypoi\easypoi.exe"
  CreateDirectory "$SMPROGRAMS\�ٶȵ�ͼPOI�ɼ�����"
  CreateShortCut "$SMPROGRAMS\�ٶȵ�ͼPOI�ɼ�����\�ٶȵ�ͼPOI�ɼ�����.lnk" "$INSTDIR\easypoi.exe"
  CreateShortCut "$DESKTOP\�ٶȵ�ͼPOI�ɼ�����.lnk" "$INSTDIR\easypoi.exe"
  File /r "..\dist\easypoi\*.*"
SectionEnd

Section -AdditionalIcons
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\�ٶȵ�ͼPOI�ɼ�����\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\�ٶȵ�ͼPOI�ɼ�����\Uninstall.lnk" "$INSTDIR\uninst.exe"
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
 *  �����ǰ�װ�����ж�ز���  *
 ******************************/

Section Uninstall
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\easypoi.exe"

  Delete "$SMPROGRAMS\�ٶȵ�ͼPOI�ɼ�����\Uninstall.lnk"
  Delete "$SMPROGRAMS\�ٶȵ�ͼPOI�ɼ�����\Website.lnk"
  Delete "$DESKTOP\�ٶȵ�ͼPOI�ɼ�����.lnk"
  Delete "$SMPROGRAMS\�ٶȵ�ͼPOI�ɼ�����\�ٶȵ�ͼPOI�ɼ�����.lnk"

  RMDir "$SMPROGRAMS\�ٶȵ�ͼPOI�ɼ�����"

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

#-- ���� NSIS �ű��༭�������� Function ���α�������� Section ����֮���д���Ա��ⰲװ�������δ��Ԥ֪�����⡣--#

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "��ȷʵҪ��ȫ�Ƴ� $(^Name) ���������е������" IDYES +2
  Abort
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) �ѳɹ��ش����ļ�����Ƴ���"
FunctionEnd
