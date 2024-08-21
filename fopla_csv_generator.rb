require 'net/http'
require 'uri'
require 'json'
require 'csv'
require 'pry'
require 'date'

class Fopla
  class << self

    API_KEY = #TOKEN

    def perform(path_to_csv)
      start_time = Time.now
      genre = path_to_csv

      isbn_array = []
      isbns_not_found = []

      complete_book_profiles = []
      incomplete_book_profiles = []
      not_found_book_profiles = []

      CSV.foreach(path_to_csv + ".csv") do |row|
        isbn_data = {
          isbn: row[0],
          category: row[1],
          binding: row[2],
          language: row[3],
          library_discard: row[4],
          comments: row[5],
        }

        # first verify input data and fail hard - manually correct the file and try again
        raise "#{row[0]} Unrecognized category #{isbn_data[:category]}" \
          unless ['fiction','nonfiction','teen','middle','picture','board','graphic novel'].include? isbn_data[:category]
          # perhaps accept cookbook here? instead of nonfiction, for a straight-up cookbook
        raise "Unrecognized binding" \
          unless ['hardcover','trade paper','board'].include? isbn_data[:binding]
          # board not really needed because it's also a category
        if !isbn_data[:language].nil?
          raise "#{row[0]} Unrecognized language #{isbn_data[:language]}" unless ['french',''].include? isbn_data[:language]
          # can add more languages as needed
        end
        if !isbn_data[:library_discard].nil?
          raise "#{row[0]} Unrecognized library discard setting" unless ['library discard'].include? isbn_data[:library_discard]
        end
        isbn_array.push(isbn_data)

      end

      isbn_array.each do |isbn|
        puts "Generating book profile for ISBN: #{isbn[:isbn]}..."
        book_profile = get(isbn[:isbn])

        if book_profile['book']
          formatted_book_profile = format(book_profile,isbn)
          case formatted_book_profile['status']
          when 'complete'
            complete_book_profiles.push(formatted_book_profile)
          else
            incomplete_book_profiles.push(formatted_book_profile)
            puts "Generated incomplete book profile for #{isbn[:isbn]}"
          end
        else
          isbns_not_found.push(isbn)
          not_found_book_profiles.push(book_profile)
          puts "Could not generate book profile for #{isbn[:isbn]}"
        end

        # flag books that require manual pricing
        if !isbn[:comments].nil?
          puts "Note special comments for #{isbn[:isbn]}: #{isbn[:comments]}"
        end

        # presumably this is to avoid hitting ISBNdb rate limits
        sleep 1
      end

      book_profile_types = {
        complete: complete_book_profiles,
        incomplete: incomplete_book_profiles,
        not_found: not_found_book_profiles
      }

      book_profile_types.each do |type, book_profiles|
        next if book_profiles.empty?
        write_to_csv(type.to_s, book_profiles, genre)
      end

      end_time = Time.now

      puts "---\nRESULTS -\nComplete Book Profiles: #{complete_book_profiles.count}\n"\
      "Incomplete Book Profiles: #{incomplete_book_profiles.count}\n"\
      "Books Not Found: #{not_found_book_profiles.count}\n---\n"\
      "Runtime: #{end_time - start_time} seconds"
    end

  private

    def get(isbn)
      endpoint = "https://api2.isbndb.com/book/#{isbn}"
      uri = URI.parse(endpoint)
      request = Net::HTTP::Get.new(uri)
      request["Accept"] = "application/json"
      request["Authorization"] = API_KEY

      req_options = {
        use_ssl: uri.scheme == "https",
      }

      response = Net::HTTP.start(uri.hostname, uri.port, req_options) do |http|
        http.request(request)
      end

      if response.code == '200'
        response = JSON.parse(response.body)
        response['errorType'] ? {} : response
      else
        {
          isbn: isbn,
          title: '*Could not find in database, error '+response.code,
          authors: '',
          publish_date: '',
          publisher: '',
          image: '',
          synopsys: '',
        }
      end
    end

    def format(book_profile,isbn_data)
      profile = book_profile['book']

      formatted_book_profile = {
        isbn: profile['isbn13'] || profile['isbn'],
        title: profile['title'] || 'N/A',
        authors: format_authors(profile),
        publish_date: format_publish_date(profile),
        publisher: profile['publisher'] || 'N/A',
        image: profile['image'] || 'N/A',
        synopsys: profile['synopsys'] || profile['overview'] || double_check_isbn_13(profile),
        weight: format_weight(profile),
        binding: format_binding(profile),
        tags: format_tags(isbn_data),
        price: format_price(isbn_data),
        library_discard: format_library_discard(isbn_data),
      }

      # check that binding from ISBNdb matches binding indicated in scan file
      compare_binding(formatted_book_profile,isbn_data)

      formatted_book_profile['status'] =
        if formatted_book_profile[:authors].downcase == 'n/a' || formatted_book_profile[:image].downcase == 'n/a'
         'incomplete'
        else
          'complete'
        end

      formatted_book_profile
    end

    def format_tags(isbn_data)
      tags = ''
      case isbn_data[:category]
      when 'fiction'
        tags = 'Fiction'
      when 'nonfiction'
        tags = 'Non-Fiction'
      when 'teen'
        tags = 'Kids,Teen'
      when 'middle'
        tags = 'Kids,Middle Grade: Ages 8-12'
      when 'picture'
        tags = 'Kids,Picture Books: Ages 3-8'
      when 'board'
        tags = 'Kids,Board Books: Ages 0-3'
      when 'graphic novel'
        tags = 'Fiction,Graphic Novel'
      end
      if !isbn_data[:language].nil? 
        case isbn_data[:language]
        when 'french'
          tags += ',French'
        end
      end
      tags
    end

    # todo there has to be a nicer data structure for this
    def format_price(isbn_data)
      case isbn_data[:category]
      when 'fiction'
        case isbn_data[:binding]
        when 'hardcover'
          if isbn_data[:library_discard].nil?
            '6.99'
          else
            '5.99'
          end
        when 'trade paper'
          if isbn_data[:library_discard].nil?
            '5.99'
          else
            # unusual and not on standardized price list
            '4.99'
            puts "#{isbn_data[:isbn]} is a library discard and trade paperback fiction - unexpected! setting price to 4.99"
          end
        end
      when 'nonfiction'
        case isbn_data[:binding]
        when 'hardcover'
          if isbn_data[:library_discard].nil?
            '7.99'
          else
            '5.99'
          end
        when 'trade paper'
          if isbn_data[:library_discard].nil?
            '5.99'
          else
            # unusual and not on standardized price list
            '4.99'
            puts "#{isbn_data[:isbn]} is a library discard and trade paperback nonfiction - unexpected! setting price to 4.99"
          end
        end
      when 'teen'
        # shortcut
        '4.99'
      when 'middle'
        case isbn_data[:binding]
        when 'hardcover'
          if isbn_data[:library_discard].nil?
            '4.99'
          else
            '3.99'
          end
        when 'trade paper'
          '3.99'
        end
      when 'picture'
        if isbn_data[:library_discard].nil?
          '4.99'
        else
          '3.99'
        end
      when 'board'
        '3.99'
      end
    end

    def format_library_discard(isbn_data)
        if !isbn_data[:library_discard].nil?
          'TRUE'
        else 
          ''
        end
    end

    def format_weight(profile)
      if profile['dimensions_structured'] && profile['dimensions_structured']['weight']
        if profile['dimensions_structured']['weight']['unit'] == 'pounds'
          weight_pounds = profile['dimensions_structured']['weight']['value']
          weight_grams = weight_pounds*454
          weight_grams_rounded = weight_grams.round()
          weight_grams_rounded
        elsif profile['dimensions_structured']['weight']['unit'] == 'g'
          profile['dimensions_structured']['weight']['value']
        else
          puts "Unsupported weight units #{profile['dimensions_structured']['weight']['unit']}, weight set to 0"
          0
        end
      else
        0
      end
    end

    def compare_binding(formatted_book_profile,isbn_data)
      case formatted_book_profile[:binding]
      when 'Hardcover'
        if isbn_data[:binding] != 'hardcover'
          puts "#{isbn_data[:isbn]} - ISBNdb says binding is hardcover but scan file says it is #{isbn_data[:binding]}."
          puts "Confirm which it is and fix product description and/or price in generated CSV."
        end
      when 'Paperback'
        if isbn_data[:binding] != 'trade paper'
          puts "#{isbn_data[:isbn]} - ISBNdb says binding is paperback but scan file says it is #{isbn_data[:binding]}."
          puts "Confirm which it is and fix product description and/or price in generated CSV."
        end
      when 'N/A'
        puts "#{isbn_data[:isbn]} - ISBNdb says binding is N/A but scan file says it is #{isbn_data[:binding]}."
        puts "Fix product description in generated CSV."
      end
    end

    def format_binding(profile)
      if profile['binding']
        if profile['binding'] == 'Hardcover' || profile['binding'] == 'Paperback'
          profile['binding']
        else
          puts "ISBNdb returns unsupported binding #{profile['binding']}, setting to N/A for now"
          'N/A'
        end
      else
        puts "ISBNdb does not return binding, setting to N/A for now"
        'N/A'
      end
    end

    # unused afaict
    def format_publish_date(profile)
      if profile['publish_date']
        Date.parse(profile['publish_date']).strftime("%m/%d/%Y")
      else
        'N/A'
      end
    rescue
      'N/A'
    end

    def format_authors(profile)
      if profile['authors'] && !profile['authors'].empty?
        profile['authors']&.compact.map do |author|
          author.split(', ').reverse.join(' ')
        end.join(', ')
      else
        'N/A'
        puts "ISBNdb does not return author, setting to N/A for now"
      end
    end

    # not sure what this is about, legacy code
    def double_check_isbn_13(profile)
      isbn_13 = profile['isbn13']
      new_profile = get(isbn_13)['book']
      new_profile['synopsys'] || new_profile['overview'] || ''
    rescue
      ''
    end

    def write_to_csv(type, book_profiles, genre)
      CSV.open(
        "#{Date.today}-FOPLA-#{type}-book-profiles-#{genre}.csv",
        'w',
        write_headers: true,
        headers: [
          'Handle',
          'Title',
          'Body (HTML)',
          'Vendor',
          'Type',
          'Tags',
          'Published',
          'Option1 Name',
          'Option1 Value',
          'Variant SKU',
          'Variant Grams',
          'Variant Inventory Tracker',
          'Variant Inventory Qty',
          'Variant Price',
          'Variant Barcode',
          'Image Src',
          'Image Position',
          'product.metafields.custom.library_discard',
        ]
      ) do |csv|
        book_profiles.each do |profile|
          csv << [
            profile[:isbn],
            profile[:title],
            generate_html_body(profile),
            profile[:authors],
            'Book',
            profile[:tags],
            'TRUE',
            'Title',
            'Default Title',
            profile[:isbn],
            profile[:weight],
            'shopify',
            '1',
            profile[:price],
            profile[:isbn],
            profile[:image],
            '1',
            profile[:library_discard],
          ]
        end
      end
    end

    # synopsys seems to always be empty - legacy code
    # I think the ISBNdb field is called synopsis (different spelling)
    # But I've looked at what comes back and it's generally too voluminous for us
    # So, ok to be ignoring it for now
    def generate_html_body(profile)
      formatted = profile[:synopsys].downcase.split(/(?<=[?.!])\s*/).map(&:capitalize).join(" ")
      "#{formatted}<strong>Publisher: </strong>#{profile[:publisher]}" \
        "<br><strong>Binding: </strong>#{profile[:binding]}"
    end
  end
end

Fopla.perform('scans')
