export function getFileIcon(fileName: string): string {
  const ext = fileName.split('.').pop()?.toLowerCase();

  switch(ext) {
    case 'jpg':
    case 'jpeg':
    case 'png':
    case 'gif':
      return '';
    case 'pdf':
      return 'fa-file-pdf';
    case 'xls':
    case 'xlsx':
      return 'fa-file-excel';
    case 'doc':
    case 'docx':
      return 'fa-file-word';
    case 'txt':
      return 'fa-file-alt';
    default:
      return 'fa-file';
  }
}

export function isImage(fileName: string): boolean {
  const ext = fileName.split('.').pop()?.toLowerCase();
  return ['jpg','jpeg','png','gif'].includes(ext ?? '');
}
