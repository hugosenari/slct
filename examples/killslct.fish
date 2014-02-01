function killslct -d "Select process to kill"
    if test (count $argv) -eq 0
        ps ax|slctp|xargs kill -9
    else
        ps ax|grep $argv|grep -v grep|slctp|xargs kill -9
    end
end