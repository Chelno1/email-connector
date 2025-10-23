"""
附件数据模型

本模块定义了邮件附件的数据结构,提供附件保存、大小计算等功能。
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class Attachment:
    """
    附件数据模型
    
    Attributes:
        filename: 附件文件名
        content_type: MIME类型(如 'application/pdf', 'image/png')
        size: 文件大小(字节)
        content: 附件二进制内容(可选,用于保存附件)
        saved_path: 附件保存路径(如果已保存)
    
    Examples:
        >>> att = Attachment(
        ...     filename="report.pdf",
        ...     content_type="application/pdf",
        ...     size=1024000,
        ...     content=b"PDF content..."
        ... )
        >>> att.get_size_mb()
        0.98
        >>> saved_path = att.save("./output/attachments")
    """
    
    filename: str
    content_type: str
    size: int
    content: Optional[bytes] = None
    saved_path: Optional[str] = None
    
    def __post_init__(self):
        """数据验证"""
        if not self.filename:
            raise ValueError("附件文件名不能为空")
        
        if not self.content_type:
            raise ValueError("附件MIME类型不能为空")
        
        if self.size < 0:
            raise ValueError("附件大小不能为负数")
    
    def to_dict(self) -> dict:
        """
        转换为字典(不包含二进制内容)
        
        Returns:
            包含附件元数据的字典
        """
        return {
            'filename': self.filename,
            'content_type': self.content_type,
            'size': self.size,
            'saved_path': self.saved_path
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Attachment':
        """
        从字典创建实例
        
        Args:
            data: 包含附件数据的字典
            
        Returns:
            Attachment实例
            
        Examples:
            >>> data = {
            ...     'filename': 'image.png',
            ...     'content_type': 'image/png',
            ...     'size': 2048
            ... }
            >>> att = Attachment.from_dict(data)
        """
        return cls(
            filename=data['filename'],
            content_type=data['content_type'],
            size=data['size'],
            content=data.get('content'),
            saved_path=data.get('saved_path')
        )
    
    def save(self, directory: str) -> str:
        """
        保存附件到指定目录
        
        Args:
            directory: 输出目录路径
            
        Returns:
            保存的完整路径
            
        Raises:
            ValueError: 如果附件内容为空
            OSError: 如果文件保存失败
            
        Examples:
            >>> att.save("./output/attachments/2024-01-15")
            './output/attachments/2024-01-15/report.pdf'
        """
        if self.content is None:
            raise ValueError("附件内容为空,无法保存")
        
        # 创建目录(如果不存在)
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # 处理文件名冲突
        base_name = self.filename
        counter = 1
        file_path = os.path.join(directory, base_name)
        
        while os.path.exists(file_path):
            name, ext = os.path.splitext(base_name)
            file_path = os.path.join(directory, f"{name}_{counter}{ext}")
            counter += 1
        
        # 保存文件
        try:
            with open(file_path, 'wb') as f:
                f.write(self.content)
            
            # 设置文件权限(仅所有者可读写)
            os.chmod(file_path, 0o600)
            
            self.saved_path = file_path
            return file_path
            
        except Exception as e:
            raise OSError(f"保存附件失败: {e}")
    
    def get_size_mb(self) -> float:
        """
        返回文件大小(MB)
        
        Returns:
            文件大小(MB),保留2位小数
            
        Examples:
            >>> att = Attachment("file.pdf", "application/pdf", 1048576)
            >>> att.get_size_mb()
            1.0
        """
        return round(self.size / (1024 * 1024), 2)
    
    def get_extension(self) -> str:
        """
        获取文件扩展名
        
        Returns:
            文件扩展名(包含点号),如 '.pdf'
            
        Examples:
            >>> att = Attachment("report.pdf", "application/pdf", 1024)
            >>> att.get_extension()
            '.pdf'
        """
        return os.path.splitext(self.filename)[1]
    
    def is_image(self) -> bool:
        """
        判断是否为图片文件
        
        Returns:
            如果是图片返回True,否则False
            
        Examples:
            >>> att = Attachment("photo.jpg", "image/jpeg", 2048)
            >>> att.is_image()
            True
        """
        return self.content_type.startswith('image/')
    
    def __repr__(self) -> str:
        """
        字符串表示
        
        Returns:
            附件的字符串表示
        """
        size_mb = self.get_size_mb()
        saved_info = f", saved='{self.saved_path}'" if self.saved_path else ""
        return (
            f"Attachment(filename='{self.filename}', "
            f"type='{self.content_type}', "
            f"size={size_mb}MB{saved_info})"
        )