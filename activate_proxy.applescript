tell application "System Preferences"
    activate
end tell

tell application "System Events"
    tell process "System Preferences"
        click menu bar item "Network" of menu bar 1 of application process "System Events"
        delay 1
        click button "Advanced" of window 1
        delay 1
        click button "Proxies" of window 1
        delay 1
        set value of checkbox "Web Proxy (HTTP)" of window 1 to true
        set value of text field 1 of window 1 to "your.proxy.server"
        set value of text field 2 of window 1 to "8080"
        -- 如果需要密码，可以添加以下行并填写密码
        -- set value of text field 3 of window 1 to "yourPassword"
        click button "OK" of window 1
        delay 1
        click button "Apply" of window 1
    end tell
end tell

quit application "System Preferences"
