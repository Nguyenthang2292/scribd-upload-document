"""
PDF Encryption Component

This module provides functionality to encrypt PDF files with password protection
and different encryption levels.
"""

import os
from typing import Optional, Dict, Any
from enum import Enum

try:
    from PyPDF4 import PdfFileReader, PdfFileWriter
except ImportError:
    from PyPDF2 import PdfFileReader, PdfFileWriter


class EncryptionLevel(Enum):
    """PDF encryption levels."""
    NONE = 0
    LOW = 1      # 40-bit RC4
    MEDIUM = 2   # 128-bit RC4
    HIGH = 3     # 128-bit AES


class PDFEncryption:
    """PDF Encryption handler for password protection and encryption."""
    
    def __init__(self):
        self.encryption_levels = {
            EncryptionLevel.NONE: 0,
            EncryptionLevel.LOW: 1,
            EncryptionLevel.MEDIUM: 2,
            EncryptionLevel.HIGH: 3
        }
    
    def encrypt_pdf(
        self,
        input_file: str,
        output_file: str,
        user_password: str = "",
        owner_password: str = "",
        encryption_level: EncryptionLevel = EncryptionLevel.MEDIUM,
        permissions: Optional[Dict[str, bool]] = None
    ) -> bool:
        """Encrypt PDF file with password protection.
        
        Args:
            input_file: Path to input PDF file
            output_file: Path to output PDF file
            user_password: Password required to open the PDF
            owner_password: Password required for full access (defaults to user_password)
            encryption_level: Level of encryption to apply
            permissions: Dictionary of permissions to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read input PDF
            with open(input_file, 'rb') as pdf_file:
                pdf_reader = PdfFileReader(pdf_file, strict=False)
                pdf_writer = PdfFileWriter()
                
                # Copy all pages
                for page_num in range(pdf_reader.getNumPages()):
                    page = pdf_reader.getPage(page_num)
                    pdf_writer.addPage(page)
                
                # Set default permissions if not provided
                if permissions is None:
                    permissions = {
                        'print': True,
                        'modify': False,
                        'copy': False,
                        'annot-forms': False
                    }
                
                # Set owner password if not provided
                if not owner_password:
                    owner_password = user_password
                
                # Apply encryption
                if encryption_level == EncryptionLevel.NONE:
                    # No encryption
                    pass
                elif encryption_level == EncryptionLevel.LOW:
                    pdf_writer.encrypt(user_password, owner_password, use_128bit=False)
                elif encryption_level == EncryptionLevel.MEDIUM:
                    pdf_writer.encrypt(user_password, owner_password, use_128bit=True)
                elif encryption_level == EncryptionLevel.HIGH:
                    # High encryption with specific permissions
                    pdf_writer.encrypt(
                        user_password, 
                        owner_password, 
                        use_128bit=True,
                        permissions_flag=self._get_permissions_flag(permissions)
                    )
                
                # Write output file
                with open(output_file, 'wb') as output_pdf:
                    pdf_writer.write(output_pdf)
            
            return True
            
        except Exception as e:
            print(f"Error encrypting PDF: {str(e)}")
            return False
    
    def decrypt_pdf(
        self,
        input_file: str,
        output_file: str,
        password: str
    ) -> bool:
        """Decrypt PDF file using password.
        
        Args:
            input_file: Path to input PDF file
            output_file: Path to output PDF file
            password: Password to decrypt the PDF
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read input PDF
            with open(input_file, 'rb') as pdf_file:
                pdf_reader = PdfFileReader(pdf_file, strict=False)
                
                # Check if PDF is encrypted
                if not pdf_reader.isEncrypted:
                    print("PDF is not encrypted")
                    return False
                
                # Try to decrypt
                try:
                    pdf_reader.decrypt(password)
                except Exception as e:
                    print(f"Failed to decrypt PDF: {str(e)}")
                    return False
                
                pdf_writer = PdfFileWriter()
                
                # Copy all pages
                for page_num in range(pdf_reader.getNumPages()):
                    page = pdf_reader.getPage(page_num)
                    pdf_writer.addPage(page)
                
                # Write output file
                with open(output_file, 'wb') as output_pdf:
                    pdf_writer.write(output_pdf)
            
            return True
            
        except Exception as e:
            print(f"Error decrypting PDF: {str(e)}")
            return False
    
    def check_encryption_status(self, pdf_file: str) -> Dict[str, Any]:
        """Check encryption status of PDF file.
        
        Args:
            pdf_file: Path to PDF file
            
        Returns:
            Dictionary containing encryption information
        """
        try:
            with open(pdf_file, 'rb') as file:
                pdf_reader = PdfFileReader(file, strict=False)
                
                info = {
                    'is_encrypted': pdf_reader.isEncrypted,
                    'file_path': pdf_file,
                    'num_pages': pdf_reader.getNumPages()
                }
                
                if pdf_reader.isEncrypted:
                    # Try to get encryption info
                    try:
                        # This might not work for all encrypted PDFs
                        info['encryption_method'] = "Unknown"
                    except:
                        info['encryption_method'] = "Unknown"
                
                return info
                
        except Exception as e:
            return {
                'error': str(e),
                'file_path': pdf_file,
                'is_encrypted': False
            }
    
    def _get_permissions_flag(self, permissions: Dict[str, bool]) -> int:
        """Convert permissions dictionary to PDF permissions flag.
        
        Args:
            permissions: Dictionary of permissions
            
        Returns:
            Integer flag representing permissions
        """
        # PDF permission flags
        PRINT = 1 << 2
        MODIFY = 1 << 3
        COPY = 1 << 4
        ANNOT_FORMS = 1 << 5
        
        flag = 0
        
        if permissions.get('print', False):
            flag |= PRINT
        if permissions.get('modify', False):
            flag |= MODIFY
        if permissions.get('copy', False):
            flag |= COPY
        if permissions.get('annot-forms', False):
            flag |= ANNOT_FORMS
        
        return flag
    
    def change_password(
        self,
        input_file: str,
        output_file: str,
        old_password: str,
        new_user_password: str,
        new_owner_password: str = ""
    ) -> bool:
        """Change password of encrypted PDF.
        
        Args:
            input_file: Path to input PDF file
            output_file: Path to output PDF file
            old_password: Current password
            new_user_password: New user password
            new_owner_password: New owner password (defaults to user password)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First decrypt
            temp_file = input_file + ".temp"
            if not self.decrypt_pdf(input_file, temp_file, old_password):
                return False
            
            # Then encrypt with new password
            if not new_owner_password:
                new_owner_password = new_user_password
            
            success = self.encrypt_pdf(
                temp_file, 
                output_file, 
                new_user_password, 
                new_owner_password
            )
            
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            return success
            
        except Exception as e:
            print(f"Error changing password: {str(e)}")
            return False


def encrypt_pdf_file(
    input_file: str,
    output_file: str,
    password: str,
    encryption_level: EncryptionLevel = EncryptionLevel.MEDIUM
) -> bool:
    """Convenience function to encrypt PDF with password.
    
    Args:
        input_file: Path to input PDF file
        output_file: Path to output PDF file
        password: Password for encryption
        encryption_level: Level of encryption
        
    Returns:
        True if successful, False otherwise
    """
    encryptor = PDFEncryption()
    return encryptor.encrypt_pdf(input_file, output_file, password, password, encryption_level)


def decrypt_pdf_file(
    input_file: str,
    output_file: str,
    password: str
) -> bool:
    """Convenience function to decrypt PDF with password.
    
    Args:
        input_file: Path to input PDF file
        output_file: Path to output PDF file
        password: Password for decryption
        
    Returns:
        True if successful, False otherwise
    """
    decryptor = PDFEncryption()
    return decryptor.decrypt_pdf(input_file, output_file, password)


def add_password_protection(
    input_file: str,
    output_file: str,
    password: str
) -> bool:
    """Add password protection to PDF file.
    
    Args:
        input_file: Path to input PDF file
        output_file: Path to output PDF file
        password: Password to protect the PDF
        
    Returns:
        True if successful, False otherwise
    """
    return encrypt_pdf_file(input_file, output_file, password, EncryptionLevel.MEDIUM)


def remove_password_protection(
    input_file: str,
    output_file: str,
    password: str
) -> bool:
    """Remove password protection from PDF file.
    
    Args:
        input_file: Path to input PDF file
        output_file: Path to output PDF file
        password: Current password
        
    Returns:
        True if successful, False otherwise
    """
    return decrypt_pdf_file(input_file, output_file, password) 