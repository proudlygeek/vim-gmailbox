if !has('python')
    echo "Error: Required vim compiled with +python"
    finish
endif

function! FetchMail()
    pyfile gmailbox.py
endfunction
