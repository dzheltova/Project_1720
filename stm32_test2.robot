*** Settings ***
Library    Process    #built-in library
#создаем экземпляр класса JTAG с именем jtag_d
Library    jtag.py      WITH NAME   jtag_d 
#подключаем библиотеку для прошивки stm
Library    flash_stm.py 

Suite Setup  Open JTAG

*** Variables ***
${JTAG_ADAPTER}     FT2232
${JTAG_VID}         0x0403
${JTAG_PID}         0x6014
${BSDL_PATH}        /home/daria/bsdl
${STM32_DEVICE_ID}  0x4BA00477
${PIN_PA5}              'PA5'
${RPI_PA5}              0
${PIN_PA6}              'PA6'
${RPI_PA6}              2
${PIN_HIGH}        1
${PIN_LOW}         0
${FIRMWARE_FILE}    blink.bin

*** Test Cases ***

Test STM32 Chip ID
    Should Be True  ${ID_MATCH}

Test STM32 PA5 HIGH
    #set STM32 pin high
    jtag_d.set_signal  ${PIN_PA5}      ${PIN_HIGH}
    #Sleep   0.1
    #Test RPI pin
    
    ${led_state_gpio}=  Get GPIO State  ${RPI_PA5} 
    Should Be Equal As Integers    ${led_state_gpio}    ${PIN_HIGH}

Test STM32 PA5 LOW
    #set STM32 pin low
    jtag_d.set_signal  ${PIN_PA5}      ${PIN_LOW}
    #Sleep   0.1
    #Test RPI pin
    
    ${led_state_gpio}=  Get GPIO State  ${RPI_PA5} 
    Should Be Equal As Integers    ${led_state_gpio}    ${PIN_LOW}

Test STM32 PA6 HIGH
    #set STM32 pin high
    jtag_d.set_signal  ${PIN_PA6}      ${PIN_HIGH}
    #Sleep   0.1
    #Test RPI pin
    
    ${led_state_gpio}=  Get GPIO State  ${RPI_PA6} 
    Should Be Equal As Integers    ${led_state_gpio}    ${PIN_HIGH}

Test STM32 PA6 LOW
    #set STM32 pin low
    jtag_d.set_signal  ${PIN_PA6}      ${PIN_LOW}
    #Sleep   0.1
    #Test RPI pin
    
    ${led_state_gpio}=  Get GPIO State  ${RPI_PA6} 
    Should Be Equal As Integers    ${led_state_gpio}    ${PIN_LOW}
    
Flash STM32 Firmware
    [Setup]     Close JTAG
    
    ${result}=      Flash Stm32     ${FIRMWARE_FILE} 
    Should Be True      ${result} 

*** Keywords ***

Open JTAG
    jtag_d.cable    ${JTAG_ADAPTER}     ${JTAG_VID}     ${JTAG_PID} 
    jtag_d.bsdl     ${BSDL_PATH} 
    ${result}=  jtag_d.detect_id   ${STM32_DEVICE_ID} 
    Set Suite Variable     ${ID_MATCH}     ${result}
    jtag_d.set_extest

Get GPIO State
    [Arguments]    ${pin}
    ${result}=    Run Process    gpio    read    ${pin}
    Log    all output: ${result.stdout}
    [Return]    ${result.stdout}
    
Close JTAG
    jtag_d.send    'RESET'
    jtag_d.quit
