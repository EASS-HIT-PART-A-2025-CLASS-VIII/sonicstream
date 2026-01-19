"use client"

import { useEffect } from "react";
import { X } from "lucide-react";

interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    children: React.ReactNode;
    title?: string;
}

export default function Modal({ isOpen, onClose, children, title }: ModalProps) {
    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === "Escape") onClose();
        };

        if (isOpen) {
            document.addEventListener("keydown", handleEscape);
            document.body.style.overflow = "hidden"; // Prevent scrolling behind modal
        }

        return () => {
            document.removeEventListener("keydown", handleEscape);
            document.body.style.overflow = "unset";
        };
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <div 
                className="absolute inset-0 bg-black/80 backdrop-blur-sm transition-opacity" 
                onClick={onClose}
            />
            
            {/* Modal Content */}
            <div className="relative bg-[#181818] border border-white/10 rounded-xl shadow-2xl w-full max-w-3xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                <div className="flex items-center justify-between p-4 border-b border-white/10">
                    <h3 className="font-bold text-white">{title || "Now Playing"}</h3>
                    <button 
                        onClick={onClose}
                        className="text-gray-400 hover:text-white transition-colors p-1 rounded-full hover:bg-white/10"
                    >
                        <X className="h-5 w-5" />
                    </button>
                </div>
                
                <div className="p-0">
                    {children}
                </div>
            </div>
        </div>
    );
}
