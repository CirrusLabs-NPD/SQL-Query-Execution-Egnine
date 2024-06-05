export const Header = ({ head, para }) => {
  return (
    <div>
      <p className="font-medium text-xl mb-2 text-[#0e3374]">{head}</p>
      <p className="text-[#6c727f]">{para}</p>
    </div>
  );
};
