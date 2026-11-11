#define AppName "Iconos"
#define AppVersion "0.1.5"
#define AppPublisher "Suite de Programas"
#define AppExeName "Iconos.exe"

[Setup]
AppId={{6E37D27B-5AE6-4CBF-9BB8-23D8B40109D8}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\Programs\Iconos
DefaultGroupName=Iconos
PrivilegesRequired=lowest
UsePreviousAppDir=yes
OutputDir=instalador
OutputBaseFilename=Iconos_Setup_V0.1.5
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=assets\Iconos_App.ico
UninstallDisplayIcon={app}\Iconos.exe
CloseApplications=yes
RestartApplications=no
DisableProgramGroupPage=yes

[Files]
Source: "dist\Iconos\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Iconos"; Filename: "{app}\Iconos.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\Iconos"; Filename: "{app}\Iconos.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; Flags: unchecked

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\App Paths\Iconos.exe"; ValueType: string; ValueName: ""; ValueData: "{app}\Iconos.exe"; Flags: uninsdeletekey

[Run]
Filename: "{app}\Iconos.exe"; Description: "Abrir Iconos"; Flags: nowait postinstall skipifsilent
