import Link from 'next/link';

const settingClasses = {
   all: 'text-center',
   active: 'text-green-600 font-medium',
   inactive: 'text-gray-700 hover:text-gray-900 font-medium',
};
interface INavButtonProps {
   content: React.ReactNode | string;
   to: string;
   status: keyof typeof settingClasses;
}

export function NavButton(props: INavButtonProps) {
   const { content, to, status } = props;
   return (
      <Link
         href={to}
         className={`${settingClasses.all} ${settingClasses[status]}`}
      >
         {content}
      </Link>
   );
}

export default NavButton;
