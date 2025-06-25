[Setup]
AppName=AllTube Downloader
AppVersion=1.0
DefaultDirName={autopf}\AllTube Downloader
DefaultGroupName=AllTube Downloader
OutputDir=output
OutputBaseFilename=AllTubeDownloaderSetup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "F:\AllTubeDownloader\dist\AllTubeDownloader.exe"; DestDir: "{app}"; Flags: ignoreversion

[Tasks]
Name: desktopicon; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Icons]
Name: "{group}\AllTube Downloader"; Filename: "{app}\AllTubeDownloader.exe"
Name: "{commondesktop}\AllTube Downloader"; Filename: "{app}\AllTubeDownloader.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\AllTubeDownloader.exe"; Description: "Launch AllTube Downloader"; Flags: nowait postinstall skipifsilent
