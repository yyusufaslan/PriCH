import platform
import psutil

# Import Windows-specific modules only if available
try:
    import win32gui
    import win32process
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

            
class PlatformUtils:
    def __init__(self):
        self.os_name = platform.system().lower()

    # Returns the name of the operating system
    def get_os_name(self):
        return self.os_name
    
    def get_active_process_name_windows(self):
        if not WIN32_AVAILABLE:
            return "Windows libraries not available"
        try:
            # Get the handle of the foreground window
            hwnd = win32gui.GetForegroundWindow()
            
            # Get the process ID of the window
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            # Get the process name
            process = psutil.Process(pid)
            return process.name()
        except Exception:
            return "Unknown error"
    
    def get_active_window_title_windows(self):
        if not WIN32_AVAILABLE:
            return "Windows libraries not available"
        try:
            # Get the handle of the foreground window
            hwnd = win32gui.GetForegroundWindow()
            
            # Get the window title
            title = win32gui.GetWindowText(hwnd)
            return title if title else "Unknown"
        except Exception:
            return "Unknown error"
    
    def get_active_process_name_linux(self):
        try:
            import subprocess
            import psutil
            
            # Get the active window ID
            result = subprocess.run(['xdotool', 'getactivewindow'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                window_id = result.stdout.strip()
                
                # Get the process ID for the window
                result = subprocess.run(['xdotool', 'getwindowpid', window_id], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    pid = int(result.stdout.strip())
                    process = psutil.Process(pid)
                    return process.name()
        except (ImportError, FileNotFoundError, subprocess.SubprocessError):
            pass
        except Exception:
            pass
        return "Unknown error"
    
    def get_active_window_title_linux(self):
        try:
            import subprocess
            
            # Get the active window title
            result = subprocess.run(['xdotool', 'getactivewindow', 'getwindowname'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except (ImportError, FileNotFoundError, subprocess.SubprocessError):
            pass
        except Exception:
            pass
        return "Unknown error"
    
    def get_active_process_name_mac(self):
        try:
            import subprocess
            import psutil
            
            # Get the active window info using AppleScript
            script = '''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                app_name = result.stdout.strip()
                return app_name
        except (ImportError, FileNotFoundError, subprocess.SubprocessError):
            pass
        except Exception:
            pass
        return "Unknown error"
    
    def get_active_window_title_mac(self):
        try:
            import subprocess
            
            # Get the active window title using AppleScript
            script = '''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
                set frontWindow to name of first window of process frontApp
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                window_title = result.stdout.strip()
                return window_title if window_title else "Unknown"
        except (ImportError, FileNotFoundError, subprocess.SubprocessError):
            pass
        except Exception:
            pass
        return "Unknown error"
    
    def get_active_process_name(self):
        """Get active process name for current platform"""
        if self.os_name == "windows":
            return self.get_active_process_name_windows()
        elif self.os_name == "linux":
            return self.get_active_process_name_linux()
        elif self.os_name == "darwin":  # macOS
            return self.get_active_process_name_mac()
        else:
            return "Unknown error"
    
    def get_active_window_title(self):
        """Get active window title for current platform"""
        if self.os_name == "windows":
            return self.get_active_window_title_windows()
        elif self.os_name == "linux":
            return self.get_active_window_title_linux()
        elif self.os_name == "darwin":  # macOS
            return self.get_active_window_title_mac()
        else:
            return "Unknown error"

    def get_all_installed_programs(self):
        if self.os_name == "windows":
            return self.get_installed_programs_windows()
        elif self.os_name == "linux":
            return self.get_all_installed_programs_linux()
        elif self.os_name == "darwin":  # macOS
            return self.get_all_installed_programs_mac()
        else:
            return []
        
    def get_all_installed_programs_windows(self):
        try:
            import winreg
            import subprocess
            
            programs = []
            
            # Method 1: Check registry for installed programs
            registry_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]
            
            for registry_path in registry_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
                        for i in range(winreg.QueryInfoKey(key)[0]):
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                        if display_name and display_name not in programs:
                                            programs.append(display_name)
                                    except (FileNotFoundError, OSError):
                                        continue
                            except (FileNotFoundError, OSError):
                                continue
                except (FileNotFoundError, OSError):
                    continue
            
            # Method 2: Use PowerShell to get installed apps
            try:
                result = subprocess.run([
                    'powershell', '-Command', 
                    'Get-WmiObject -Class Win32_Product | Select-Object Name | ForEach-Object { $_.Name }'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line.strip() and line.strip() not in programs:
                            programs.append(line.strip())
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                pass
            
            # Method 3: Check Program Files directories
            program_dirs = [
                r"C:\Program Files",
                r"C:\Program Files (x86)"
            ]
            
            for program_dir in program_dirs:
                try:
                    import os
                    if os.path.exists(program_dir):
                        for item in os.listdir(program_dir):
                            if item not in programs:
                                programs.append(item)
                except (OSError, PermissionError):
                    continue
            
            return sorted(list(set(programs)))
            
        except Exception:
            return []
    def get_installed_programs_windows(self):
        try:
            import winreg
            import subprocess
            
            programs = []
            
            # Method 1: Check registry for installed programs
            programs = []
            reg_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",  # 64-bit
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"  # 32-bit
            ]

            # Hem HKEY_LOCAL_MACHINE hem HKEY_CURRENT_USER'ı kontrol et
            hives = [(winreg.HKEY_LOCAL_MACHINE, "HKEY_LOCAL_MACHINE"),
                    (winreg.HKEY_CURRENT_USER, "HKEY_CURRENT_USER")]

            for hive, hive_name in hives:
                for path in reg_paths:
                    try:
                        key = winreg.OpenKey(hive, path)
                        for i in range(0, winreg.QueryInfoKey(key)[0]):
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                subkey = winreg.OpenKey(key, subkey_name)
                                name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                                programs.append(name)
                            except FileNotFoundError:
                                continue
                            except OSError:
                                continue
                            except Exception:
                                continue
                    except FileNotFoundError:
                        continue

            return sorted(set(programs))
        except Exception:
            return []
        
    def get_all_installed_programs_linux(self):
        try:
            import subprocess
            import os
            
            programs = []
            
            # Method 1: Check package managers
            package_managers = [
                # Debian/Ubuntu
                (['dpkg', '--list'], lambda output: [line.split()[1] for line in output.split('\n')[5:] if line.strip()]),
                # Red Hat/Fedora
                (['rpm', '-qa'], lambda output: [line.split('-')[0] for line in output.split('\n') if line.strip()]),
                # Arch Linux
                (['pacman', '-Q'], lambda output: [line.split()[0] for line in output.split('\n') if line.strip()]),
                # SUSE
                (['zypper', 'packages', '--installed'], lambda output: [line.split('|')[1].strip() for line in output.split('\n')[2:] if '|' in line and line.strip()])
            ]
            
            for cmd, parser in package_managers:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        parsed_programs = parser(result.stdout)
                        programs.extend(parsed_programs)
                except (subprocess.SubprocessError, subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            # Method 2: Check common application directories
            app_dirs = [
                '/usr/bin',
                '/usr/local/bin',
                '/opt',
                '/snap/bin',
                '/var/lib/flatpak/exports/bin'
            ]
            
            for app_dir in app_dirs:
                try:
                    if os.path.exists(app_dir):
                        for item in os.listdir(app_dir):
                            if os.path.isfile(os.path.join(app_dir, item)) and item not in programs:
                                programs.append(item)
                except (OSError, PermissionError):
                    continue
            
            # Method 3: Check desktop files
            desktop_dirs = [
                '/usr/share/applications',
                '/usr/local/share/applications',
                os.path.expanduser('~/.local/share/applications')
            ]
            
            for desktop_dir in desktop_dirs:
                try:
                    if os.path.exists(desktop_dir):
                        for item in os.listdir(desktop_dir):
                            if item.endswith('.desktop'):
                                # Extract name from .desktop file
                                try:
                                    with open(os.path.join(desktop_dir, item), 'r', encoding='utf-8') as f:
                                        for line in f:
                                            if line.startswith('Name='):
                                                name = line.split('=', 1)[1].strip()
                                                if name and name not in programs:
                                                    programs.append(name)
                                                break
                                except (OSError, UnicodeDecodeError):
                                    continue
                except (OSError, PermissionError):
                    continue
            
            return sorted(list(set(programs)))
            
        except Exception:
            return []
    
    def get_all_installed_programs_mac(self):   
        try:
            import subprocess
            import os
            
            programs = []
            
            # Method 1: Check Applications folder
            app_dirs = [
                '/Applications',
                os.path.expanduser('~/Applications')
            ]
            
            for app_dir in app_dirs:
                try:
                    if os.path.exists(app_dir):
                        for item in os.listdir(app_dir):
                            if item.endswith('.app'):
                                app_name = item.replace('.app', '')
                                if app_name not in programs:
                                    programs.append(app_name)
                except (OSError, PermissionError):
                    continue
            
            # Method 2: Use system_profiler
            try:
                result = subprocess.run([
                    'system_profiler', 'SPApplicationsDataType'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if ':' in line and not line.startswith(' ') and not line.startswith('\t'):
                            app_name = line.split(':')[0].strip()
                            if app_name and app_name not in programs:
                                programs.append(app_name)
            except (subprocess.SubprocessError, subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Method 3: Use mdfind to find applications
            try:
                result = subprocess.run([
                    'mdfind', 'kMDItemKind == Application'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            app_name = os.path.basename(line).replace('.app', '')
                            if app_name and app_name not in programs:
                                programs.append(app_name)
            except (subprocess.SubprocessError, subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Method 4: Check Homebrew packages
            try:
                result = subprocess.run([
                    'brew', 'list'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.strip() and line.strip() not in programs:
                            programs.append(line.strip())
            except (subprocess.SubprocessError, subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            return sorted(list(set(programs)))
            
        except Exception:
            return []
    