<?php
if(!empty($_FILES['file'])){
    $targetDir = 'uploads/';
    $filename = basename($_FILES['file']['name']);
    $targetFilePath = $targetDir.$filename;
    if(move_uploaded_file($_FILES['file']['tmp_name'], $targetFilePath)){
        echo 'File Uploaded';
    }
}
?>