$path = "docs\" #Target directory for converting Word files
$word_app = New-Object -ComObject Word.Application

#Convert .doc and .docx to .pdf
Get-ChildItem -Path $path -Filter *.doc? | ForEach-Object {
    $document = $word_app.Documents.Open($_.FullName)
    $pdf_filename = "$($_.DirectoryName)\$($_.BaseName).pdf"
    $document.SaveAs([ref] $pdf_filename, [ref] 17)
    $document.Close()
}
$word_app.Quit()