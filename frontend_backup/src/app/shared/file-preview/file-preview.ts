import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { getFileIcon, isImage } from '../utils/file-utils';


@Component({
  selector: 'app-file-preview',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './file-preview.html',
  styleUrls: ['./file-preview.css']
})
export class FilePreviewComponent {
  @Input() files: any[] = [];

  getIcon(name: string) {
    return getFileIcon(name);
  }

  isImage(name: string) {
    return isImage(name);
  }
}
