declare module 'lucide-react' {
  import { ComponentType, SVGProps } from 'react';
  
  export interface IconProps extends SVGProps<SVGSVGElement> {
    size?: number | string;
    color?: string;
    strokeWidth?: number | string;
  }
  
  export const Plus: ComponentType<IconProps>;
  export const Send: ComponentType<IconProps>;
  export const Clock: ComponentType<IconProps>;
  export const CheckCircle: ComponentType<IconProps>;
  export const XCircle: ComponentType<IconProps>;
  export const AlertCircle: ComponentType<IconProps>;
  export const FileText: ComponentType<IconProps>;
  export const Building2: ComponentType<IconProps>;
  export const Calendar: ComponentType<IconProps>;
  export const Search: ComponentType<IconProps>;
  export const Download: ComponentType<IconProps>;
  export const Eye: ComponentType<IconProps>;
  export const Users: ComponentType<IconProps>;
  export const Target: ComponentType<IconProps>;
  export const TrendingUp: ComponentType<IconProps>;
  export const ArrowLeft: ComponentType<IconProps>;
  export const Star: ComponentType<IconProps>;
}
