function pslct -d "Select process id"
    if test (count $argv) -eq 0
        ps ax|slctp
    else
        ps ax|grep $argv|grep -v grep|slctp
    end
end