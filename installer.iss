; ============================================================
; 다문화 정보 허브 — Inno Setup 설치 스크립트
; 사전 조건: build.bat 실행하여 dist\michub 생성
; 컴파일: Inno Setup에서 이 파일 열고 컴파일
; ============================================================

#define AppName "다문화 정보 허브"
#define AppNameEn "Multicultural Info Hub"
#define AppVersion "0.1.0"
#define AppPublisher "MiHub"
#define AppExeName "michub.exe"

[Setup]
AppId={{D9A3F1E2-4B5C-6D7E-8F9A-0B1C2D3E4F5A}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppNameEn}
DefaultGroupName={#AppName}
OutputDir=installer_output
OutputBaseFilename=MiHub_Setup_{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; UninstallDisplayIcon={app}\{#AppExeName}
PrivilegesRequired=lowest
DisableProgramGroupPage=yes

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"

[Tasks]
Name: "desktopicon"; Description: "바탕화면에 바로가기 생성"; GroupDescription: "추가 작업:"
Name: "startupicon"; Description: "시작 시 자동 실행"; GroupDescription: "추가 작업:"; Flags: unchecked

[Files]
Source: "dist\michub\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
Name: "{app}\data"; Permissions: users-full

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Registry]
; 시작 시 자동 실행 (선택)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
  ValueType: string; ValueName: "MiHub"; ValueData: """{app}\{#AppExeName}"""; \
  Flags: uninsdeletevalue; Tasks: startupicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "다문화 정보 허브 실행"; Flags: nowait postinstall skipifsilent
