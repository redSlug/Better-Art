import sys, os, random, shutil, re
from custom_junk_images import JunkImages


class MechanicalTurk:
    def __init__(self, ids_to_breed=None):
        ids_to_breed = None

    #
    #
    # These methods are for preparing the experiments for mechanical turk
    #
    #

    @staticmethod
    def _get_unique_file_names(dir_path):
        unique_file_names = []

        file_sizes_dict = {}                        # used to get unique files; structure synth bug creates many of same
        for f in os.listdir(dir_path):
            if f.endswith(".png"):
                file_size = os.path.getsize(dir_path + "/" + f)
                if file_size not in file_sizes_dict:
                    unique_file_names.append(f)
                    file_sizes_dict[file_size] = True
        return unique_file_names

    @staticmethod
    def _get_experiment_number():
        dir_path = os.getcwd()
        n = 0
        for f in os.listdir(dir_path):
            if 'experiment_' in f:
                n += 1
        #print "n=", n
        return n

    @staticmethod
    def _get_html_row(name_arr, n, experiment_num):         # each row has 3 images; expecting 3 filenames
        img_url_path = 'https://users.soe.ucsc.edu/~bjdettme/f/%d/' % experiment_num
        # begin row
        s = '\t\t\t<tr>\n'

        # columns
        for name in name_arr:
            s += '\t\t\t\t<td><label for="checkbox%d"><img alt="%s" src="%s%s"/></label></td>\n' % (n, name[:-4], img_url_path, name)
            s += '\t\t\t\t<td><input id="checkbox%d" name="selected" type="checkbox" value="%s"/></td>\n' % (n, name[:-4])
            n += 1

        # end row
        return s + '\t\t\t</tr>\n'

    def generate_experiment_html(self, source_dir=None):
        if not source_dir:
            dir_path = os.getcwd() + "/" + sys.argv[1]                              # path to directory of files
        else:
            dir_path = os.getcwd() + "/" + source_dir
        current_experiment_number = self._get_experiment_number()

        template_f_name = 'mech_turk_template.html'
        unique_file_names = self._get_unique_file_names(dir_path)
        #print "there are %d unique files in %s" % (len(unique_file_names), dir_path)
        random.shuffle(unique_file_names)

        with open(template_f_name) as f:
            content = f.readlines()

        for i in range(0, len(unique_file_names), 120):
            new_f_content = ""
            first_image_index = i
            last_image_index = len(unique_file_names) - 1

            current_experiment_number += 1                                      # start at 1
            new_f_name = 'experiment_' + str(current_experiment_number) + '.html'

            inserting_auto_generated_content = False
            for line in content:
                new_f_content += line

                if "<! -- AUTO GENERATED P TAG STARTS HERE -->" in line:
                    n_i = int(len(unique_file_names) * .1) + 1   # prompts user to select 10 percent or more
                    new_f_content += '\t\t\t\t<p>Please select %d or more images that you like the best. In some cases a solid image is accidentally rendered. Please ignore erroneous output.</p>\n' % n_i

                if "<! -- AUTO GENERATED CODE STARTS HERE -->" in line:
                    inserting_auto_generated_content = True
                if inserting_auto_generated_content:
                    # create rows
                    for i in range(first_image_index, last_image_index+1, 3):
                        new_f_content += self._get_html_row(unique_file_names[i:i+3], i+1, current_experiment_number)
                    inserting_auto_generated_content = False
            f = open(new_f_name, 'w')
            f.write(new_f_content)
            f.close()
            print "created %s with %d files" % (new_f_name, len((unique_file_names)))

    #
    #
    # These methods are for analyzing the experimental results mechanical turk
    #
    #

    @staticmethod
    def _get_source_file_data(experiment_source_file):
        with open(experiment_source_file, 'r') as f:
            content = f.readlines()
        num_needed = None
        beg_of_line_specifying_min = "				<p>Please select "
        result_maxtrix = []
        for line in content:
            if not num_needed and line.startswith(beg_of_line_specifying_min):
                num_needed = int(line[len(beg_of_line_specifying_min):].split()[0])
            if "<tr>" in line:
                result_maxtrix.append([])
            if "<td><input" in line:
                img_id = re.match('.+value=\"(.+)\"', line).groups()[0]
                result_maxtrix[-1].append(img_id)
        return num_needed, result_maxtrix

    @staticmethod
    def _append_workers_result(workers_result, worker_id, img_matrix):
        pattern_view = '\n\t\t\t\t\t<div style="display: table-cell">worker: %d<br />' % worker_id
        for row in img_matrix:
            for col in row:
                if col[0] in workers_result:
                    pattern_view += ' x '
                    col[1] += " %d " % worker_id
                else:
                    pattern_view += ' - '
                    col[1] += " - "
            pattern_view += '<br />'
        pattern_view += '</div>\n'
        return pattern_view

    def _get_and_print_ids_to_breed(self, count_to_breed=14, experiment_num=None, jids=[], meta_info=''): # because 14*(14-1)/2 = 91
        expected_num = 0
        if experiment_num:
            expected_num, img_matrix = self._get_source_file_data('experiment_' + str(experiment_num) + '.html')

        img_result_matrix = []
        for row in img_matrix:
            img_result_matrix.append([])
            for col in row:
                img_result_matrix[-1].append([col, ''])

        all_worker_patterns = '\n\t\t\t\t<div style="width: 100%; display: table;">'
        all_worker_patterns += self._append_workers_result(jids, 0, img_result_matrix)

        # get header HTML
        result_description = ''
        with open('results', 'r') as f:
            content = f.readlines()

        all_ids = []
        invalid_count = 0
        invalidated_worker_ids = ''
        for i, line in enumerate(content):  # for each worker
            # first assume valid
            worker_valid = True
            # each line processes the results of a worker
            line.strip()
            workers_result = (line.strip()).split('|')
            all_worker_patterns += self._append_workers_result(workers_result, i+1, img_result_matrix)
            if len(workers_result) < expected_num:
                if worker_valid:
                    worker_valid = False
                    invalid_count += 1
                invalidated_worker_ids += ' %d (min req not met),    ' % (i+1)
                continue    # skips next line
            for img_id in workers_result:
                if img_id in jids:
                    if worker_valid:
                        worker_valid = False
                        invalid_count += 1
                    invalidated_worker_ids += ' %d (clicked blank img), ' % (i+1)
            all_ids.extend(workers_result)
        result_description += "invalid worker ids = %s<br />" % invalidated_worker_ids
        result_description += "%d invalid submission(s) out of %d total<br />" % (invalid_count, len(content))
        result_description += "%s<br />" % meta_info

        ids_dict = {}
        for item in all_ids:
            if item not in ids_dict:
                ids_dict[item] = 0
            ids_dict[item] += 1
        ids_to_breed = []

        print "\nid: vote_count"
        print "\t", ids_dict # sorted(list(ids_dict))

        print "\nvote_count: id_count"
        quant_dict = {}
        for item in ids_dict:
            cur_value = ids_dict[item]
            if ids_dict[item] not in quant_dict:
                quant_dict[cur_value] = 0
            quant_dict[cur_value] += 1
        print "\t", quant_dict

        reversed_vote_counts = reversed(list(quant_dict))
        min_vote_count = 0
        id_count = 0
        for quant_votes in reversed_vote_counts:
            id_count += quant_dict[quant_votes]
            if id_count >= count_to_breed:
                min_vote_count = quant_votes
                break

        print "\nid: vote_count > %d or (vote_count == 5 and chosen randomly to breed)" % min_vote_count
        candidate_ids = []
        for item in ids_dict:
            if ids_dict[item] > min_vote_count:
                print "\t", item, ids_dict[item]
                ids_to_breed.append(item)
            if ids_dict[item] == min_vote_count:
                candidate_ids.append(item)
        random.shuffle(candidate_ids)
        while len(ids_to_breed) < 10:
            lucky_pic = candidate_ids.pop()
            print "\t", lucky_pic, ids_dict[lucky_pic]
            ids_to_breed.append(lucky_pic)
        self.ids_to_breed = ids_to_breed

        print img_result_matrix

        self.generate_result_html(result_description, all_worker_patterns + '\n\t\t\t\t</div>\n', img_result_matrix, ids_to_breed, experiment_num)

    def generate_result_html(self, result_description, patterns_div, img_result_matrix, ids_to_breed, experiment_num):
        template_f_name = 'mech_turk_template.html'
        with open(template_f_name) as f:
            content = f.readlines()

        new_f_content = ""

        inserting_auto_generated_content = False
        for line in content:
            if '            <div class="panel-heading"><strong>Instructions</strong></div>' in line:
                new_f_content += '            <div class="panel-heading"><strong>Results</strong></div>'
            else:
                new_f_content += line
            if "<! -- AUTO GENERATED P TAG STARTS HERE -->" in line:
                new_f_content += '\t\t\t\t<p>%s</p>\n' % result_description
                new_f_content += patterns_div

            if "<! -- AUTO GENERATED CODE STARTS HERE -->" in line:
                inserting_auto_generated_content = True
            if inserting_auto_generated_content:
                # create rows
                n = 0
                for row in img_result_matrix:
                    new_f_content += self._get_result_html_row(n, row, ids_to_breed, experiment_num)
                    n += 3
                inserting_auto_generated_content = False
        new_f_name = 'exp_%s_results.html' % experiment_num
        f = open(new_f_name, 'w')
        f.write(new_f_content)
        f.close()

    @staticmethod
    def _get_result_html_row(n, arr, ids_to_breed, experiment_num):         # each row has 3 images; expecting 3 filenames
        img_url_path = 'https://users.soe.ucsc.edu/~bjdettme/f/%s/' % experiment_num
        #img_url_path = ''
        # begin row
        s = '\t\t\t<tr>\n'

        # columns
        for img_field in arr:
            results_field = img_field[1]
            border_size = 1
            if img_field[0] in ids_to_breed:
                border_size = 4
            s += '\t\t\t\t<td style="border: %dpx solid midnightblue">%s<label for="checkbox%d"><img alt="%s" src="%s%s.png"/></label></td>\n' % (border_size, results_field, n, img_field[0], img_url_path, img_field[0])
            n += 1

        # end row
        return s + '\t\t\t</tr>\n'

    def process_results(self, dir_to_obtain_selected_pics, experiment_num):
        ji = JunkImages()
        meta_info = "dir_to_obtain_selected_pics: %s, experiment_num: %s" % (dir_to_obtain_selected_pics, experiment_num)
        #print meta_info
        junk_image_ids = ji.retrieve_names_of_junk_files(dir_to_obtain_selected_pics)
        jids = [x[:-4] for x in junk_image_ids] # remove the last 4 chars (.png) from each id.
        self._get_and_print_ids_to_breed(14, experiment_num, jids, meta_info)

        cwd = os.getcwd()
        cwd_len = len(cwd)
        source_path = cwd + '/' + dir_to_obtain_selected_pics + '/'
        dest_path = source_path + 'wow/'

        print "\ncopying chosen files from %s to %s" % (source_path, dest_path)
        for img_id in self.ids_to_breed:
            full_source_path = source_path + img_id + '.png'
            full_dest_path = dest_path + img_id + '.png'
            print "\tcopying from %s to %s" % (full_source_path[cwd_len:], full_dest_path[cwd_len:])
            shutil.copyfile(full_source_path, full_dest_path)

        print "desired files are in", dest_path, ". now run:\npython evolve.py crossover", dir_to_obtain_selected_pics + "/wow/"


if __name__ == "__main__":
    # being run directly / not imported
    print "\nTo generate html, identify a directory with pngs and:"
    print "\n\tpython mechanical_turk.py g <directory_name>"
    print "\n\tpython mechanical_turk.py g gen/gen"
    print "\n\nTo process results, make sure ids are in results file and:"
    print "\n\tpython mechanical_turk.py p <directory_name> <experiment_num>\n\n"

    m = MechanicalTurk()

    cmd = sys.argv[1]
    if cmd == 'g':
        #ji = JunkImages()
        #ji.add_junk_images_to_dir(sys.argv[2])
        m.generate_experiment_html(sys.argv[2])
    elif cmd == 'p':
        m.process_results(sys.argv[2], sys.argv[3])
