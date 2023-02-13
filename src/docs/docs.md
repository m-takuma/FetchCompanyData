```mermaid
flowchart TD
    main
    mode[modeを決める]
    form_code[取得する書類を決める]
    date[検索日時を決める]
    seccode[取得する証券コードlistを指定する]
    whether_mode{APIモードである}
    fetch_docs[edinetから条件一致の書類一覧を取得する]
    download_docs[書類をダウンロードする]
    find_all_xbrldocs[xbrlフォルダを全て取得する]
    main --> mode
    mode --> form_code
    form_code --> date
    date --> seccode
    seccode --> whether_mode
    whether_mode -->|YES|fetch_docs
    fetch_docs --> download_docs
    download_docs --> find_all_xbrldocs
    whether_mode -->|NO|find_all_xbrldocs

    parse
    file_paths["指定されたディレクトリのxbrlファイルのpath"]
    parse_files[全てのファイルを解析する]
    move_dir[解析しおわったフォルダを移動する]
    parse-->file_paths
    file_paths-->parse_files
    parse_files-->move_dir
    

