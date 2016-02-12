#Relay States
HIGH Relay OFF

LOW Relay ON

#Script logic
1. Check to see if the pid exists
    - if it does, exit

2. Check relay state
    - Should be HIGH

3. Unlock the door

4. Check replay state
    - Should be LOW

5. Hold door open for X seconds

6. Lock the door

7. Check replay state
    - Should be HIGH

8. Exit

#Failure
On fail the script should log the issue and exit.
 - Try to recover to a locked state.
 - Log the issue
 - Flesh Leds dislaying the error code


#Error Code
- edit the pid file with the error numbers on the first line and the error
  message on the second
- flash the red led to the number error code


The Red Led on error will flash to display the error codes:

- Each flash consists of being held high for 500ms and low for 500ms

- Hold led high for 1 second (Start of the error code)

- Hold Low for 1 second

- the second part is the replay that failed the check
    - 1 flash being the first
    - 2 flashes being the second
    - 3 flashes being both

- Hold Low for 1 second

- first part is where in the script it failed
    - 1 flash being the first check
    - 2 flashes being the second check
    - 3 flashes being the third check

- Hold Low for 1 second

website will also look for the pid file and display the error code and message
to the user instead of the html form. (This check will happen on both GET and
POST)

