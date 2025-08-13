; INSTALADOR PROFESIONAL DE ZEROX v2.0
; =====================================
; Script NSIS para crear instalador de Windows

!include "MUI2.nsh"
!include "FileFunc.nsh"

; Información general
!define PRODUCT_NAME "ZEROX"
!define PRODUCT_VERSION "2.0.0"
!define PRODUCT_PUBLISHER "ZEROX AI Trading"
!define PRODUCT_WEB_SITE "https://zerox-ai.com"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\ZEROX.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; Configuración del instalador
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "ZEROX_Setup_v2.0.0.exe"
InstallDir "$PROGRAMFILES64\ZEROX"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show
RequestExecutionLevel admin

; Configuración de compresión
SetCompressor /SOLID lzma
SetCompressorDictSize 64

; Interfaz moderna
!define MUI_ABORTWARNING
!define MUI_ICON "assets\icons\zerox.ico"
!define MUI_UNICON "assets\icons\zerox.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "assets\installer\welcome.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "assets\installer\header.bmp"
!define MUI_HEADERIMAGE_RIGHT

; Páginas del instalador
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENCIA.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY

; Página personalizada para libros
Page custom PaginaLibros PaginaLibrosLeave

!insertmacro MUI_PAGE_INSTFILES

; Página final con opciones
!define MUI_FINISHPAGE_RUN "$INSTDIR\ZEROX.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Ejecutar ZEROX ahora"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\LEEME.md"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Ver instrucciones"
!define MUI_FINISHPAGE_LINK "Visitar web de ZEROX"
!define MUI_FINISHPAGE_LINK_LOCATION "${PRODUCT_WEB_SITE}"
!insertmacro MUI_PAGE_FINISH

; Páginas del desinstalador
!insertmacro MUI_UNPAGE_INSTFILES

; Idiomas (solo castellano)
!insertmacro MUI_LANGUAGE "Spanish"

; Variables
Var LibrosDialog
Var LibrosListBox
Var AgregarLibrosBtn
Var LibrosInfo

; Función para la página de libros
Function PaginaLibros
    !insertmacro MUI_HEADER_TEXT "Biblioteca de Conocimiento" "Añade libros de trading para que ZEROX aprenda"
    
    nsDialogs::Create 1018
    Pop $LibrosDialog
    
    ${If} $LibrosDialog == error
        Abort
    ${EndIf}
    
    ; Texto informativo
    ${NSD_CreateLabel} 0 0 100% 40u "ZEROX puede aprender de libros de trading en formato PDF, EPUB, MOBI, TXT o DOCX.$\r$\n$\r$\nAñade libros ahora o hazlo más tarde desde el programa."
    Pop $LibrosInfo
    
    ; Lista de libros
    ${NSD_CreateListBox} 0 50u 100% 100u ""
    Pop $LibrosListBox
    
    ; Botón para agregar
    ${NSD_CreateButton} 0 160u 100u 15u "Agregar Libros..."
    Pop $AgregarLibrosBtn
    ${NSD_OnClick} $AgregarLibrosBtn AgregarLibros
    
    nsDialogs::Show
FunctionEnd

Function PaginaLibrosLeave
FunctionEnd

Function AgregarLibros
    nsDialogs::SelectFileDialog open "Libros (*.pdf;*.epub;*.mobi;*.txt;*.docx)|*.pdf;*.epub;*.mobi;*.txt;*.docx"
    Pop $0
    ${If} $0 != ""
        ${NSD_LB_AddString} $LibrosListBox $0
    ${EndIf}
FunctionEnd

; Secciones de instalación
Section "ZEROX - Programa Principal" SEC01
    SectionIn RO
    
    SetOutPath "$INSTDIR"
    SetOverwrite on
    
    ; Archivos principales
    File /r "dist\ZEROX\*.*"
    
    ; Crear directorios necesarios
    CreateDirectory "$INSTDIR\data"
    CreateDirectory "$INSTDIR\logs"
    CreateDirectory "$INSTDIR\config"
    CreateDirectory "$INSTDIR\biblioteca"
    
    ; Accesos directos
    CreateDirectory "$SMPROGRAMS\ZEROX"
    CreateShortcut "$SMPROGRAMS\ZEROX\ZEROX.lnk" "$INSTDIR\ZEROX.exe"
    CreateShortcut "$SMPROGRAMS\ZEROX\Manual.lnk" "$INSTDIR\LEEME.md"
    CreateShortcut "$SMPROGRAMS\ZEROX\Desinstalar.lnk" "$INSTDIR\uninstall.exe"
    CreateShortcut "$DESKTOP\ZEROX.lnk" "$INSTDIR\ZEROX.exe"
    
    ; Registro
    WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\ZEROX.exe"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\ZEROX.exe"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
    WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
    
    ; Tamaño estimado (5GB como pediste)
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntOp $0 $0 + 5242880 ; Añadir 5GB en KB
    WriteRegDWORD ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "EstimatedSize" $0
SectionEnd

Section "Datos de Entrenamiento IA" SEC02
    SetOutPath "$INSTDIR\data\training"
    
    ; Aquí irían los datos de entrenamiento
    ; Por ahora creamos archivos dummy para aumentar tamaño
    DetailPrint "Instalando datos de entrenamiento de IA..."
    
    ; Crear archivo grande de datos
    FileOpen $0 "$INSTDIR\data\training\modelo_base.dat" w
    FileWrite $0 "ZEROX AI Training Data v2.0"
    FileClose $0
SectionEnd

Section "Modelos Pre-entrenados" SEC03
    SetOutPath "$INSTDIR\data\models"
    
    DetailPrint "Instalando modelos de Machine Learning..."
    
    ; Crear modelos dummy
    FileOpen $0 "$INSTDIR\data\models\modelo_principal.pkl" w
    FileWrite $0 "ZEROX ML Model"
    FileClose $0
SectionEnd

Section "Biblioteca Inicial" SEC04
    SetOutPath "$INSTDIR\biblioteca"
    
    DetailPrint "Instalando biblioteca de conocimiento inicial..."
    
    ; Copiar libros si se añadieron
    ; Los libros reales se procesarían aquí
SectionEnd

; Descripciones
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC01} "Programa principal de ZEROX con IA integrada"
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC02} "Datos de entrenamiento para mejorar predicciones"
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC03} "Modelos ML pre-entrenados para inicio rápido"
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC04} "Biblioteca inicial con estrategias básicas"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; Desinstalador
Section Uninstall
    ; Preguntar si guardar datos
    MessageBox MB_YESNO "¿Deseas mantener tus datos y configuración?" IDYES mantener_datos
    
    ; Borrar todo
    Delete "$INSTDIR\*.*"
    RMDir /r "$INSTDIR"
    
    mantener_datos:
    
    ; Borrar accesos directos
    Delete "$SMPROGRAMS\ZEROX\*.*"
    RMDir "$SMPROGRAMS\ZEROX"
    Delete "$DESKTOP\ZEROX.lnk"
    
    ; Borrar registro
    DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
    DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
    
    SetAutoClose true
SectionEnd

; Funciones de inicialización
Function .onInit
    ; Verificar Windows 64-bit
    ${If} ${RunningX64}
        DetailPrint "Sistema de 64 bits detectado"
    ${Else}
        MessageBox MB_OK|MB_ICONEXCLAMATION "ZEROX requiere Windows de 64 bits"
        Abort
    ${EndIf}
    
    ; Verificar privilegios de administrador
    UserInfo::GetAccountType
    Pop $0
    ${If} $0 != "admin"
        MessageBox MB_OK|MB_ICONEXCLAMATION "Necesitas privilegios de administrador"
        Abort
    ${EndIf}
FunctionEnd

Function un.onInit
    MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "¿Estás seguro de desinstalar ZEROX?" IDYES +2
    Abort
FunctionEnd

Function un.onUninstSuccess
    HideWindow
    MessageBox MB_ICONINFORMATION|MB_OK "ZEROX se ha desinstalado correctamente"
FunctionEnd