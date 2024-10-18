#  **0xInjector**

0xInjector is a simple and efficient tool for injecting DLLs into Windows processes. This project is developed in Python and uses the Flet library to create a user-friendly graphical interface.

## **Features**

- **List Processes**: Displays a list of currently running processes on the system, allowing easy selection of the target process.
- **Select DLL**: Allows the user to select a DLL file for injection.
- **DLL Injection**: Performs the injection of the DLL into the selected process, with the option to wait for the remote thread to finish.
- **Visual Feedback**: Shows the status of the operation and the results of the injection through the interface.

## **Requirements**

To run 0xInjector, you will need the following components:

- Python 3.x
- Flet library
- psutil library

You can install the required libraries using pip:

```
pip install flet psutil
```

## **Usage**

1. Clone this repository:
   ```
   git clone https://github.com/your_username/0xInjector.git
   cd 0xInjector
   ```

2. Run the script:
   ```
   python 0xInjector.py
   ```

3. In the graphical interface:
   - Select a process from the list or enter the PID manually.
   - Click "Select DLL" to choose the DLL file you wish to inject.
   - If desired, check the "Wait for Remote Thread to Finish" option.
   - Click "Inject DLL" to inject the DLL into the selected process.
   - The result of the operation will be displayed below.

## **Code Structure**

The code is organized as follows:

- **list_processes**: Function that lists currently running processes.
- **inject_dll**: Function that performs the DLL injection into the specified process.
- **inject_dll_click**: Function called when the "Inject DLL" button is clicked.
- **refresh_process_list**: Updates the list of available processes.
- **on_dll_selected**: Callback that updates the interface with the selected DLL.
- **main**: Initializes the graphical interface using Flet.

## **License**

This project is licensed under the MIT License.

## **Contributions**

Contributions are welcome! Feel free to open issues or pull requests.

## **Disclaimer**

DLL injection can be considered a hacking practice and should be used responsibly and only on processes that you own or have permission to modify. The author is not responsible for any misuse of the tool.
