nmap <cr> :w\|:call RunTest()<cr>
nmap ,p :!python3<cr>

function RunTest()
    let module = substitute(expand('%:t'), ".py", "", "g")

    if module =~ "test"
        let test_module = module
    else
        let test_module = "test_" . module
    endif

    if filereadable("test/".test_module.".py")
        echo system("python3 -B -m unittest test.".test_module)
    endif
endfunction

autocmd BufWritePost *.py silent! !black --quiet % 2>/dev/null

let g:ctrlp_custom_ignore = '__pycache__\|__init__.py\|DS_Store\|git'
