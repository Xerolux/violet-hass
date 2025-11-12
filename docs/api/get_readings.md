# getReadings – erwartete Werte (aus XLSX konvertiert)


## SYSTEM INFORMATIONS

- **date** [TT.MM.YYYY] — System-date (incl. time-zone offsets)
- **time** [HH:MM:SS] — System-time (incl. time-zone offsets)
- **CPU_TEMP** [FLOAT] — CPU-Temperature, system (°C)
- **CPU_TEMP_CARRIER** [FLOAT] — CPU-Temperature, Carrier-Board (°C)
- **CPU_UPTIME** [DD HH MM] — System uptime since last boot
- **SYSTEM_MEMORY** [FLOAT] — Overall System-memory used (mb)
- **SYSTEM_memoryusage** [FLOAT] — System-memory used by App (mb)
- **SYSTEM_dosagemodule_cpu_temperature** [FLOAT] — CPU-Temperature, Dosing-Module (°C)
- **SW_VERSION** [STRING (X.X.X)] — Software-Version VIOLET application
- **SW_VERSION_CARRIER** [STRING (X.X.X)] — Firmware-Version VIOLET carrier

## ANALOG SESNORS

- **ADC1_value** [FLOAT] — Reading of AnalogSensor_1 (preassure)
- **ADC2_value** [FLOAT] — Reading of AnalogSensor_2 (overflow vessel level)
- **ADC3_value** [FLOAT] — Reading of AnalogSensor_3 (4..20mA)
- **ADC4_value** [FLOAT] — Reading of AnalogSensor_4 (4..20mA)
- **ADC5_value** [FLOAT] — Reading of AnalogSensor_5 (0-10V)

## IMPULS INPUTS

- **IMP1_value** [FLOAT] — Reading of Impuls_Input 1 (Flow switch)
- **IMP2_value** [FLOAT] — Reading of Impuls_Input 2 (Flow Pump)

## TEMPERATRUE SENSORS

- **onewire1_state** [STRING] — Fault state of this 1wire sensor
- **onewire1_rcode** [STRING] — ROM-Code of this 1wire sensor
- **onewire1_value** [FLOAT] — Current reading of this 1wire sensor (°C)
- **onewire1_value_max** [FLOAT] — Todays max. value of this sensor (resetted every night at 00:00)
- **onewire1_value_min** [FLOAT] — Todays min. value of this sensor (resetted every night at 00:00)
- **…** — all 1wire sensors (1-12) are handled the same 
- **onewire12_state** [see above] — Fault state of this 1wire sensor
- **onewire12_rcode** — ROM-Code of this 1wire sensor
- **onewire12_value** — Current reading of this 1wire sensor (°C)
- **onewire12_value_max** — Todays max. value of this sensor (resetted every night at 00:00)
- **onewire12_value_min** — Todays min. value of this sensor (resetted every night at 00:00)

## WATER PARAMETERS

- **orp_value** [FLOAT] — Current ORP reading (in mV)
- **orp_value_max** [FLOAT] — min. ORP reading of this day (resetted every night at 00:00)
- **orp_value_min** [FLOAT] — max. ORP reading of this day (resetted every night at 00:00)
- **pH_value** [FLOAT] — Current pH reading
- **pH_value_max** [FLOAT] — min. pH reading of this day (resetted every night at 00:00)
- **pH_value_min** [FLOAT] — max. pH reading of this day (resetted every night at 00:00)
- **pot_value** [FLOAT] — Current chlorine reading (in mg/l … ppm)
- **pot_value_max** [FLOAT] — min. Cl reading of this day (resetted every night at 00:00)
- **pot_value_min** [FLOAT] — max. Cl reading of this day (resetted every night at 00:00)

## DOSING OPTIONS / AMOUNTS

- **DOS_1_CL** [INTEGER] — Current state of OUTPUT: CL-DOSING
- **DOS_1_CL_DAILY_DOSING_AMOUNT_ML** [INTEGER] — Todays dosing amount in ml (resetted to "0" at 00:00 every night)
- **DOS_1_CL_LAST_CAN_RESET** [Unix epoch (milliseconds)] — Unix Epoch of last Can_Reset
- **DOS_1_CL_LAST_OFF** [Unix epoch (seconds)] — Epoch of last OFF-switching
- **DOS_1_CL_LAST_ON** [Unix epoch (seconds)] — Epoch of last ON-switching
- **DOS_1_CL_RUNTIME** [HH:MM:SS] — Daily runtime of CL_DOSING output
- **DOS_1_CL_STATE** [LIST, STRING] — Array of possible blockings
- **DOS_1_CL_TOTAL_CAN_AMOUNT_ML** [INTEGER] — Remaining can amount in ml
- **DOS_1_CL_TYPE** [INTEGER] — Indicates if the dosing controller is based on ORP only or ORP and Chlorine values
- **DOS_1_CL_USE** [INTEGER] — Indicates if this Dosing option is activated in overall system-config or not
- **DOS_2_ELO** [see above] — Current state of OUTPUT: ELO-DOSING (relay-extension)
- **…** — all other "DOS_2_ELO" options are the same as DOS_1_CL 
- **DOS_4_PHM** [see above] — Current state of OUTPUT: pH- DOSING 
- **…** — all other "DOS_4_PHM" options are the same as DOS_1_CL 
- **DOS_5_PHP** [see above] — Current state of OUTPUT: pH+ DOSING 
- **…** — all other "DOS_5_PHP" options are the same as DOS_1_CL 
- **DOS_6_FLOC** [see above] — Current state of OUTPUT: FLOC DOSING 
- **…** — all other "DOS_6_FLOC" options are the same as DOS_1_CL 

## DIGITAL INPUTS

- **INPUT1** [INTEGER] — Current state of this Digital-Input
- **…** — all Inputs (1-12) are handled the same 
- **INPUT12** [INTEGER] — Current state of this Digital-Input
- **INPUT_CE1** [INTEGER] — Current state of can empty-switch contact
- **INPUT_CE2** [INTEGER] — Current state of can empty-switch contact
- **INPUT_CE3** [INTEGER] — Current state of can empty-switch contact
- **INPUT_CE4** [INTEGER] — Current state of can empty-switch contact

## STATES OF SWITCHING RULES

- **DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_1** [INTEGER] — State of Switching-rule 1
- **…** — every rule (1-7) is handled the same
- **DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_7** [INTEGER] — State of Switching-rule 7
- **DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH1** [FLOAT] — If rule is active and has a timer: remaining runtime in secods till it gets stopped
- **…** — every rule (1-7) is handled the same
- **DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH7** [FLOAT] — If rule is active and has a timer: remaining runtime in secods till it gets stopped

## STATES OF DMX LIGHT-SZENES

- **DMX_SCENE1** [INTEGER] — State of DMX-LIGHTSZENE 1
- **…** — every scene (1-12) is handled the same
- **DMX_SCENE12** [INTEGER] — State of DMX-LIGHTSZENE 12

## STATES / RUNTIMES OF OUTPUTS

- **PUMP** [INTEGER] — Current state of PUMP output
- **PUMP_LAST_OFF** [Unix epoch (seconds)] — Epoch of last OFF-switching
- **PUMP_LAST_ON** [Unix epoch (seconds)] — Epoch of last ON-switching
- **PUMP_RUNTIME** [HH MM SS] — Daily runtime of this output
- **PUMP_RPM_0** [INTEGER] — Current state of PUMP_STOP output
- **PUMP_RPM_0_LAST_OFF** — Values are present but not used. They will always have 00:00:00 as value

## "PUMP_RPM_0_LAST_ON"

- **PUMP_RPM_0_RUNTIME** [HH MM SS] — Daily runtime of this output
- **PUMP_RPM_1** [INTEGER] — Current state of PUMP_RPM_1 (Speed 1) output
- **PUMP_RPM_1_LAST_OFF** — Values are present but not used. They will always have 00:00:00 as value

## "PUMP_RPM_1_LAST_ON"

- **PUMP_RPM_1_RUNTIME** [HH MM SS] — Daily runtime of this output
- **PUMP_RPM_2** [INTEGER] — Current state of PUMP_RPM_2 (Speed 2) output
- **PUMP_RPM_2_LAST_OFF** — Values are present but not used. They will always have 00:00:00 as value

## "PUMP_RPM_2_LAST_ON"

- **PUMP_RPM_2_RUNTIME** [HH MM SS] — Daily runtime of this output
- **PUMP_RPM_3** [INTEGER] — Current state of PUMP_RPM_3 (Speed 3) output
- **PUMP_RPM_3_LAST_OFF** — Values are present but not used. They will always have 00:00:00 as value

## "PUMP_RPM_3_LAST_ON"

- **PUMP_RPM_3_RUNTIME** [HH MM SS] — Daily runtime of this output
- **SOLAR** [INTEGER] — Current state of SOLAR output
- **SOLAR_LAST_OFF** [Unix epoch (seconds)] — Epoch of last OFF-switching
- **SOLAR_LAST_ON** [Unix epoch (seconds)] — Epoch of last ON-switching
- **SOLAR_RUNTIME** [HH MM SS] — Daily runtime of this output
- **HEATER** [INTEGER] — Current state of HEATER output
- **HEATER_LAST_OFF** [Unix epoch (seconds)] — Epoch of last OFF-switching
- **HEATER_LAST_ON** [Unix epoch (seconds)] — Epoch of last ON-switching
- **HEATER_RUNTIME** [HH MM SS] — Daily runtime of this output
- **HEATER_POSTRUN_TIME** [FLOAT] — Remaining time (in seconds) for possibly running HEATER-Postrun timer. 
- **LIGHT** [INTEGER] — Current state of LIGHT output
- **LIGHT_LAST_OFF** [Unix epoch (seconds)] — Epoch of last OFF-switching
- **LIGHT_LAST_ON** [Unix epoch (seconds)] — Epoch of last ON-switching
- **LIGHT_RUNTIME** [HH MM SS] — Daily runtime of this output
- **REFILL** [INTEGER] — Current state of REFILL output
- **REFILL_LAST_OFF** [Unix epoch (seconds)] — Epoch of last OFF-switching
- **REFILL_LAST_ON** [Unix epoch (seconds)] — Epoch of last ON-switching
- **REFILL_RUNTIME** [HH MM SS] — Daily runtime of this output
- **ECO** [INTEGER] — Current state of ECO-MODE output
- **ECO_LAST_OFF** [Unix epoch (seconds)] — Epoch of last OFF-switching
- **ECO_LAST_ON** [Unix epoch (seconds)] — Epoch of last ON-switching
- **ECO_RUNTIME** [HH MM SS] — Daily runtime of this output
- **BACKWASH** [INTEGER] — State of BACKWASH output
- **BACKWASH_LAST_OFF** [Unix epoch (seconds)] — Time of last OFF-switching
- **BACKWASH_LAST_ON** [Unix epoch (seconds)] — Time of last ON-switching
- **BACKWASH_RUNTIME** [HH MM SS] — Daily runtime of BACKWASH output
- **BACKWASHRINSE** [INTEGER] — State of BACKWASH-RINSE output
- **BACKWASHRINSE_LAST_OFF** [Unix epoch (seconds)] — Time of last OFF-switching
- **BACKWASHRINSE_LAST_ON** [Unix epoch (seconds)] — Time of last ON-switching
- **BACKWASHRINSE_RUNTIME** [HH MM SS] — Daily runtime of BACKWASHRINSE output

## COVER STATE

- **COVER_STATE** [STRING] — Current state of the Cover (as plain text)

## STATES / RUNTIMES OF OUTPUTS ON RELAY-EXTENSION

- **EXT1_1** [INTEGER] — Current state of EXT1_1 output (1st Relay on relay-extension)
- **EXT1_1_LAST_OFF** [Unix epoch (seconds)] — Epoch of last OFF-switching
- **EXT1_1_LAST_ON** [Unix epoch (seconds)] — Epoch of last ON-switching
- **EXT1_1_RUNTIME** [HH MM SS] — Daily runtime of this output
- **…** — all outputs (EXT1_1 - EXT1_8) are hadled the same
- **EXT1_8** [INTEGER] — Current state of EXT1_8 output (8th Relay on relay-extension)
- **EXT1_8_LAST_OFF** [Unix epoch (seconds)] — Epoch of last OFF-switching
- **EXT1_8_LAST_ON** [Unix epoch (seconds)] — Epoch of last ON-switching
- **EXT1_8_RUNTIME** [HH MM SS] — Daily runtime of this output

## SOME OTHER STATES

- **OVERFLOW_DRYRUN_STATE** [STRING] — Indicates a triggered dryrun (PUMP STOPPED) from Overflow vessel control
- **OVERFLOW_OVERFILL_STATE** [STRING] — Indicates a triggered overfill (PUMP TURNED ON) from Overflow vessel control
- **OVERFLOW_REFILL_STATE** [STRING] — Indicates a triggered refill from Overflow vessel control
- **BACKWASH_DELAY_RUNNING** [STRING] — Indicates if backwash should run, but can not be done (i.e. because of manual pump switching)
- **BACKWASH_DELAY_TIMESTAMP** [Unix epoch (seconds)] — Starttime (timestamp) since when backwash is delayed
- **BACKWASH_LAST_AUTO_RUN** [Unix epoch (seconds)] — Epoch of last automatic BACKWASH
- **BACKWASH_LAST_MANUAL_RUN** [Unix epoch (seconds)] — Epoch of last manual BACKWASH
- **BACKWASH_OMNI_MOVING** [STRING] — Inidcates a moviong OMNI
- **BACKWASH_OMNI_STATE** [STRING] — Possibly fault-state of an OMNI
- **BACKWASH_STEP** [INTEGER] — Current step the whole backwash process is in
- **BACKWASH_STATE** [STRING] — indicates current state of a backwash process
- **BATHING_AI_SURVEILLANCE_STATE** [STRING] — Indicates if bathing-surveillance has detected a level change in the overflow vessel
- **BATHING_AI_START_LEVEL** [FLOAT] — if surveillance is running, this is the start water-level to compare against 
- **BATHING_AI_LAST_LEVEL** [FLOAT] — the current water-level in the overflow vessel
- **BATHING_AI_PUMP_STATE** [STRING] — Indicates if bathing surveillance switched the pump on or not
- **BATHING_AI_PUMP_TIMESTAMP** [Unix epoch (seconds)] — Indicates at what time bathing surveillance switched the pump on
- **PVSURPLUS** [INTEGER] — Indicates if the PV-Surplus function was triggered and how it was triggered