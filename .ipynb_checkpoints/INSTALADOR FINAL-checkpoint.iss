; INSTALADOR PROFESIONAL DE ZEROX v2.0 (Inno Setup)
; ===============================================
; Script de Inno Setup 6.4.3 para crear instalador de ZEROX en Windows

[Setup]
AppName=ZEROX                        
; Nombre de la aplicación que se instalará (se muestra al usuario)
AppVersion=2.0.0                     
; Versión de la aplicación
AppPublisher=ZEROX AI Trading        
; Empresa o autor de la aplicación
DefaultDirName={pf}\ZEROX            
; Carpeta de instalación por defecto ({pf} = "Archivos de Programa" en 64 bits)
DefaultGroupName=ZEROX               
; Nombre del grupo de accesos directos en Menú Inicio
OutputBaseFilename=ZEROX_Setup_v2.0.0
; Nombre del archivo instalador que se generará (EXE de salida)
SetupIconFile=assets\icons\zerox.ico 
; Icono del instalador (mostrado en el archivo EXE y en la ventana de instalación)
Compression=lzma2                    
; Método de compresión (lzma2 para alta compresión)
SolidCompression=yes                 
; Activa la compresión sólida para reducir el tamaño del instalador
PrivilegesRequired=admin             
; Requiere que el instalador se ejecute con privilegios de administrador (UAC)
ArchitecturesAllowed=x64             
; Permite instalar **solo** en sistemas Windows de 64 bits
ArchitecturesInstallIn64BitMode=x64  
; Usa modo de instalación 64 bits (archivos en Program Files de 64 bits)
CreateUninstallRegKey=no             
; Desactiva la creación automática de la entrada de desinstalación (la añadiremos manualmente en [Registry])
LicenseFile=LICENCIA.txt             
; Archivo de licencia a mostrar durante la instalación (página de Licencia)
WizardImageFile=assets\installer\welcome.bmp    
; Imagen BMP mostrada en la página de bienvenida (y final) del asistente
WizardSmallImageFile=assets\installer\header.bmp
; Imagen BMP pequeña para el encabezado de las páginas del asistente

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"  
; Idioma de la instalación: Español

[Components]
Name: "main"; Description: "Programa principal de ZEROX con IA integrada"; Types: full; Flags: fixed
; ^ Componente principal (obligatorio, no se puede desmarcar) - contiene la aplicación principal
Name: "training"; Description: "Datos de entrenamiento para mejorar predicciones"; Types: full; ExtraDiskSpaceRequired: 5368709120
; ^ Componente opcional: datos de entrenamiento de IA (reserva ~5 GB de espacio en disco en la estimación)
Name: "models"; Description: "Modelos ML pre-entrenados para inicio rápido"; Types: full
; ^ Componente opcional: modelos de Machine Learning pre-entrenados
Name: "library"; Description: "Biblioteca inicial con estrategias básicas"; Types: full
; ^ Componente opcional: biblioteca de libros/estrategias iniciales

[Dirs]
Name: "{app}"; Components: main                       
; Directorio base de instalación ({app} = la ruta elegida por el usuario)
Name: "{app}\data"; Components: main                  
; Crear carpeta "data" para datos de IA
Name: "{app}\logs"; Components: main                  
; Crear carpeta "logs" para archivos de registro
Name: "{app}\config"; Components: main                
; Crear carpeta "config" para configuraciones
Name: "{app}\biblioteca"; Components: main            
; Crear carpeta "biblioteca" para los libros de trading
Name: "{app}\data\training"; Components: training     
; Crear subcarpeta "data\training" si se instalan datos de entrenamiento
Name: "{app}\data\models"; Components: models         
; Crear subcarpeta "data\models" si se instalan modelos pre-entrenados

[Files]
Source: "dist\ZEROX\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: main
; ^ Archivos principales de la aplicación (se toma todo el contenido de la carpeta "dist\ZEROX")
Source: "LEEME.md"; DestDir: "{app}"; Flags: ignoreversion; Components: main
; ^ Archivo de instrucciones o manual (LEEME.md) incluido con la aplicación
; Notas: Los datos de entrenamiento y modelos pre-entrenados no se especifican aquí como archivos 
;        porque en este ejemplo se crearán archivos de ejemplo durante la instalación (ver [Code]).

[Icons]
Name: "{group}\ZEROX"; Filename: "{app}\ZEROX.exe"; WorkingDir: "{app}"; IconFilename: "{app}\ZEROX.exe"
; ^ Acceso directo en Menú Inicio para ejecutar ZEROX
Name: "{group}\Manual (LEEME)"; Filename: "{app}\LEEME.md"; WorkingDir: "{app}"
; ^ Acceso directo en Menú Inicio para abrir el manual/instrucciones (archivo LEEME.md)
Name: "{group}\Desinstalar ZEROX"; Filename: "{uninstallexe}"; IconFilename: "{uninstallexe}"
; ^ Acceso directo en Menú Inicio para desinstalar ZEROX
Name: "{commondesktop}\ZEROX"; Filename: "{app}\ZEROX.exe"; WorkingDir: "{app}"; IconFilename: "{app}\ZEROX.exe"
; ^ Acceso directo en el Escritorio para ejecutar ZEROX (visible para todos los usuarios)

[Registry]
; Registrar la ruta de la aplicación para poder ejecutarla desde el diálogo "Ejecutar" de Windows
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\ZEROX.exe"; ValueType: string; ValueData: "{app}\ZEROX.exe"; Flags: uninsdeletekey

; Crear la entrada de desinstalación en el registro (Método explícito y seguro)
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZEROX"; ValueName: "DisplayName"; ValueType: string; ValueData: "ZEROX 2.0.0"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZEROX"; ValueName: "DisplayVersion"; ValueType: string; ValueData: "2.0.0"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZEROX"; ValueName: "Publisher"; ValueType: string; ValueData: "ZEROX AI Trading"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZEROX"; ValueName: "URLInfoAbout"; ValueType: string; ValueData: "https://zerox-ai.com"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZEROX"; ValueName: "DisplayIcon"; ValueType: string; ValueData: "{app}\ZEROX.exe"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\ZEROX"; ValueName: "UninstallString"; ValueType: string; ValueData: """{uninstallexe}"""

[Run]
Filename: "{app}\ZEROX.exe"; Description: "Ejecutar ZEROX ahora"; Flags: nowait postinstall skipifsilent
; ^ Opción para ejecutar ZEROX al finalizar la instalación (aparece como casilla marcada en la página final)
Filename: "{app}\LEEME.md"; Description: "Ver instrucciones"; Flags: postinstall shellexec skipifsilent unchecked
; ^ Opción para abrir el archivo LEEME (manual) al finalizar (casilla opcional sin marcar por defecto)
Filename: "https://zerox-ai.com"; Description: "Visitar web de ZEROX"; Flags: postinstall shellexec skipifsilent unchecked
; ^ Opción para visitar la página web oficial al finalizar la instalación (casilla opcional)

[Code]
// ***Sección de código Pascal para personalizar el asistente e instalar archivos especiales***

var
  BooksPage: TWizardPage;
  BookList: TNewListBox;
  AddButton: TNewButton;
  InfoLabel: TLabel;
  KeepData: Boolean;
  
procedure AddBooksButtonClick(Sender: TObject);
var 
  FileName: String;
begin
  { Mostrar un cuadro de diálogo para seleccionar un archivo de libro }
  if GetOpenFileName('Seleccione un libro de trading para agregar', FileName, '', 
     'Libros (*.pdf;*.epub;*.mobi;*.txt;*.docx)|*.pdf;*.epub;*.mobi;*.txt;*.docx|Todos los archivos (*.*)|*.*', '') then
  begin
    ;// Si el usuario selecciona un archivo y no cancela, se agrega la ruta a la lista
    BookList.Items.Add(FileName);
  end;
end;

procedure InitializeWizard();
begin
  { Crear una página personalizada después de la selección de directorio, para agregar libros de trading }
  BooksPage := CreateCustomPage(wpSelectDir, 'Biblioteca de Conocimiento', 
    'Añade libros de trading para que ZEROX aprenda'); 
  ;// Crea una página personalizada titulada "Biblioteca de Conocimiento"
  
  { Agregar una etiqueta con información en la página personalizada }
  InfoLabel := TLabel.Create(BooksPage.Surface);
  InfoLabel.Caption := 'ZEROX puede aprender de libros de trading en formato PDF, EPUB, MOBI, TXT o DOCX.' 
                       + #13#10 + #13#10 
                       + 'Añade libros ahora o hazlo más tarde desde el programa.'; 
  ;// Texto explicativo con saltos de línea (#13#10 representa una nueva línea)
  InfoLabel.Left := ScaleX(0);
  InfoLabel.Top := ScaleY(0);
  InfoLabel.Width := BooksPage.SurfaceWidth;
  InfoLabel.Height := ScaleY(40);
  InfoLabel.Parent := BooksPage.Surface;  ;// Ajustamos posición/tamaño y añadimos al formulario de la página
  
  { Agregar una lista (ListBox) para mostrar los libros seleccionados }
  BookList := TNewListBox.Create(BooksPage.Surface);
  BookList.Left := ScaleX(0);
  BookList.Top := ScaleY(50);
  BookList.Width := BooksPage.SurfaceWidth;
  BookList.Height := ScaleY(100);
  BookList.Parent := BooksPage.Surface;
  
  { Agregar un botón "Agregar Libros..." para abrir un diálogo de selección de archivos }
  AddButton := TNewButton.Create(BooksPage.Surface);
  AddButton.Caption := 'Agregar Libros...';
  AddButton.Left := ScaleX(0);
  AddButton.Top := ScaleY(160);
  AddButton.Width := ScaleX(100);
  AddButton.Height := ScaleY(21);
  AddButton.Parent := BooksPage.Surface;
  AddButton.OnClick := @AddBooksButtonClick;  
  // Asocia la función AddBooksButtonClick al evento de clic del botón
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  i: Integer;
  src, dest: String;
begin
  { Esta función se llama en varios puntos del proceso de instalación }
  if CurStep = ssPostInstall then begin
    ;// ssPostInstall: justo después de que la instalación de archivos estándar haya finalizado
    //{ Copiar los libros seleccionados a la carpeta "{app}\biblioteca" }
    if BookList.Items.Count > 0 then begin
      for i := 0 to BookList.Items.Count - 1 do begin
        src := BookList.Items[i];   ;// Ruta de origen del libro (en el disco del usuario)
        dest := ExpandConstant('{app}\biblioteca\') + ExtractFileName(src);
        if FileCopy(src, dest, False) then
          Log('Libro copiado: ' + src + ' -> ' + dest)
        else
          Log('**Error al copiar libro: ' + src);
        ;// Se copian los archivos de libros seleccionados al directorio de la biblioteca del programa
      end;
    end;
    { Crear archivos dummy (vacíos o de ejemplo) para datos de entrenamiento y modelos, si se seleccionaron }
    if WizardIsComponentSelected('training') then begin
      ;// Si el usuario seleccionó el componente "Datos de Entrenamiento IA"
      SaveStringToFile(ExpandConstant('{app}\data\training\modelo_base.dat'), 'ZEROX AI Training Data v2.0', False);
      ;// Crea un archivo "modelo_base.dat" con contenido de ejemplo en la carpeta de training
      Log('Datos de entrenamiento instalados (archivo modelo_base.dat creado)');
    end;
    if WizardIsComponentSelected('models') then begin
      ;// Si el usuario seleccionó el componente "Modelos Pre-entrenados"
      SaveStringToFile(ExpandConstant('{app}\data\models\modelo_principal.pkl'), 'ZEROX ML Model', False);
      ;// Crea un archivo "modelo_principal.pkl" de ejemplo en la carpeta de modelos
      Log('Modelo pre-entrenado instalado (archivo modelo_principal.pkl creado)');
    end;
  end;
end;

function InitializeUninstall(): Boolean;
begin
  { Preguntar confirmación al iniciar la desinstalación }
  if MsgBox('¿Estás seguro de desinstalar ZEROX?', mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDNO then
  begin
    Result := False;   ;// Si el usuario responde "No", cancelamos la desinstalación
    exit;
  end;
  { Preguntar si desea mantener datos y configuraciones }
  if MsgBox('¿Deseas mantener tus datos y configuración?', mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then
    KeepData := True   // El usuario quiere conservar sus datos personales (logs, configuración, biblioteca, etc.)
  else
    KeepData := False;
  Result := True;  ;// Continuar con la desinstalación
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then begin
    ;// usUninstall: justo antes de empezar a eliminar los archivos instalados
    if KeepData then begin
      MsgBox('Se conservarán tus datos personales (registros, configuraciones, biblioteca, etc.)', mbInformation, MB_OK);
      ;// Informamos que los datos del usuario se mantendrán
    end else begin
      ;// El usuario no desea mantener datos: procedemos a borrarlos manualmente 
      DelTree(ExpandConstant('{app}\data'), True, True, True);
      DelTree(ExpandConstant('{app}\logs'), True, True, True);
      DelTree(ExpandConstant('{app}\config'), True, True, True);
      DelTree(ExpandConstant('{app}\biblioteca'), True, True, True);
      ;// Elimina por completo las carpetas de datos, logs, config y biblioteca (con todo su contenido)
    end;
  end;
end;

procedure DeinitializeUninstall();
begin
  { Mostrar mensaje al finalizar la desinstalación }
  MsgBox('ZEROX se ha desinstalado correctamente', mbInformation, MB_OK);
end;
