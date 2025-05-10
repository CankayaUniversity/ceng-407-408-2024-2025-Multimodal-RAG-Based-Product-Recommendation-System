import React from 'react';
import { Heart } from 'lucide-react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-100 py-8 mt-16">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p className="text-gray-700 text-sm">
              © {new Date().getFullYear()} Fashion Recommendation System. All rights reserved.
            </p>
          </div>
          <div className="flex items-center text-sm text-gray-600">
            <span className="mr-1">Made with</span>
            <Heart size={14} className="text-red-500 mx-1" />
            <span>by Team 4</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 